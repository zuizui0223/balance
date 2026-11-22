#!/usr/bin/env Rscript
# 2025 original trial data: read the EXACT published Zenodo data.csv.
# Source model fixed before fitting, from published paper Methods:
# negative-binomial nbinom2 mixed model, recipient position, species,
# log visit duration, log donor release, trial random intercept.
# Recipient rows are NOT independent donor experiments.
args <- commandArgs(trailingOnly=TRUE)
if(length(args)!=2L) {
  stop("Usage: Rscript replay_vasquez_2025_recipient_curve.R ORIGINAL_ZENODO_CSV OUT_DIR")
}
path<-args[[1L]]
out<-args[[2L]]
dir.create(out,recursive=TRUE,showWarnings=FALSE)
suppressPackageStartupMessages(library(glmmTMB))
suppressPackageStartupMessages(library(digest))
check<-"484ed52ac611dbc6dc1831320a6c54d314492e9830823edd8934690c35205b79"
if(digest::digest(path,algo="sha256",file=TRUE)!=check)
  stop("Not original published Zenodo donor/recipient source bytes")
d<-read.csv(path,stringsAsFactors=FALSE,check.names=FALSE)
expected<-c("trial_number","bee_hive","bee_ID","flower_sp","recipient",
            "duration_visit","pollen_stigma","donor_released",
            "donor_remaining","donor_total")
stopifnot(identical(names(d),expected),
          nrow(d)==60L,length(unique(d$trial_number))==15L,
          setequal(d$recipient,c(1,2,3,4)),
          setequal(d$flower_sp,c("S.dulcamara","S.rostratum")),
          all(is.finite(d$pollen_stigma)),all(d$pollen_stigma>=0),
          all(is.finite(d$duration_visit)),all(d$duration_visit>0),
          all(is.finite(d$donor_released)),all(d$donor_released>0),
          !anyNA(d[,expected]))
trial_n<-table(d$trial_number)
if(!all(trial_n==4L))stop("Original 15 donor trials lack exact four recipients")
for(trial in unique(d$trial_number)) {
  subset<-d[d$trial_number==trial,,drop=FALSE]
  if(!setequal(subset$recipient,1:4) ||
     length(unique(subset$bee_ID))!=1L ||
     length(unique(subset$flower_sp))!=1L ||
     any(vapply(c("donor_total","donor_released","donor_remaining"),
       function(k)max(subset[[k]])-min(subset[[k]])>0.01,logical(1)))) {
    stop("A donor source is not constant over four recipients")
  }
}
d$trial_number <- factor(d$trial_number)
d$flower_sp <- factor(d$flower_sp,levels=c("S.dulcamara","S.rostratum"))
# Two originally described models only: recipient×species optional interaction.
forms<-list(
  additive=pollen_stigma ~ recipient + flower_sp + log(duration_visit) +
    log(donor_released) + (1|trial_number),
  interaction=pollen_stigma ~ recipient*flower_sp + log(duration_visit) +
    log(donor_released) + (1|trial_number)
)
results<-list()
coefficients<-list()
for(model in names(forms)) {
  warn<-character()
  fit<-NULL
  error<-""
  tryCatch(withCallingHandlers({
    fit<-glmmTMB(forms[[model]],data=d,family=nbinom2(link="log"),
                 REML=FALSE,na.action=na.fail)
  },warning=function(w){
    warn<<-c(warn,conditionMessage(w))
    invokeRestart("muffleWarning")
  }),error=function(e){error<<-conditionMessage(e)})
  if(is.null(fit)) stop(paste("Original-source",model,"GLMM failed:",error))
  good<-nobs(fit)==60L && fit$fit$convergence==0L &&
      isTRUE(fit$sdr$pdHess) &&
      all(is.finite(summary(fit)$coefficients$cond))
  if(!good) stop(paste("Original-source",model,"GLMM failed convergence/Hessian/count"))
  mat<-summary(fit)$coefficients$cond
  coefficients[[model]]<-data.frame(
    model=model,term=rownames(mat),estimate=mat[,1],
    se=mat[,2],z=mat[,3],p=mat[,4],row.names=NULL)
  rv<-VarCorr(fit)$cond
  results[[model]]<-data.frame(
    model=model,n_recipient_rows=nobs(fit),
    n_independent_donor_bee_trials=nlevels(d$trial_number),
    n_original_hives=length(unique(d$bee_hive)),
    aic=AIC(fit),log_likelihood=as.numeric(logLik(fit)),
    nbinom2_dispersion=sigma(fit),
    trial_random_intercept_variance=unname(rv[["trial_number"]][1,1]),
    optimizer_convergence=fit$fit$convergence,
    positive_definite_hessian=isTRUE(fit$sdr$pdHess),
    warnings=paste(unique(warn),collapse="; "),
    status="ORIGINAL_SOURCE_MODEL_REPLAY_NOT_ARCHITECTURE_CAUSAL_EFFECT"
  )
  if(model=="additive") {
    for(term in c("recipient","flower_spS.rostratum",
                  "log(duration_visit)","log(donor_released)")) {
      if(!(term %in% rownames(mat)))stop("Published source model lacks required coefficient")
      v<-mat[term,]
      cat(sprintf("VASQUEZ_2025_NB_REPLAY|term=%s|beta=%+.8f|se=%.8f|z=%+.8f|p=%.8g\n",
                  term, v[1],v[2],v[3],v[4]))
    }
  }
}
models<-do.call(rbind,results)
coefs<-do.call(rbind,coefficients)
aic_additive<-models$aic[models$model=="additive"]
aic_interaction<-models$aic[models$model=="interaction"]
if(length(aic_additive)!=1L||length(aic_interaction)!=1L)stop("AIC invalid")
r_slope<-subset(coefs,model=="additive"&term=="recipient")
sp_effect<-subset(coefs,model=="additive"&term=="flower_spS.rostratum")
source<-data.frame(
  author_published_recipient_slope=-0.339,
  replayed_recipient_slope=r_slope$estimate,
  original_author_species_rostratum_relative_log_effect=-0.954,
  replayed_species_rostratum_relative_log_effect=sp_effect$estimate,
  original_AIC_additive=794.8,actual_AIC_additive=aic_additive,
  original_AIC_interaction=796.6,actual_AIC_interaction=aic_interaction,
  AIC_interaction_minus_additive=aic_interaction-aic_additive,
  slope_close_to_published=abs(r_slope$estimate+.339)<0.15,
  species_effect_close_to_published=abs(sp_effect$estimate+.954)<0.25,
  exact_author_R_4_1_environment_reproduced=FALSE,
  source_csv_sha256=check,
  no_15_trial_paternity_fitness=TRUE
)
write.csv(models,file.path(out,"recipient_nb_model_diagnostics.csv"),row.names=FALSE)
write.csv(coefs,file.path(out,"recipient_nb_model_coefficients.csv"),row.names=FALSE)
write.csv(source,file.path(out,"recipient_nb_published_comparison.csv"),row.names=FALSE)
writeLines(c(capture.output(sessionInfo()),paste("glmmTMB",packageVersion("glmmTMB")),
             paste("TMB",packageVersion("TMB"))),
           file.path(out,"recipient_nb_r_session.txt"))
cat(sprintf(
  "VASQUEZ_2025_NB_MODEL|additive_AIC=%.6f|interaction_AIC=%.6f|delta_AIC=%.6f|recipient_slope=%+.8f|species_slope=%+.8f|source_model_reproduction_status=%s\n",
  aic_additive,aic_interaction,aic_interaction-aic_additive,
  r_slope$estimate,sp_effect$estimate,
  if(source$slope_close_to_published && source$species_effect_close_to_published)
    "SAME_DIRECTION_APPROX_ORIGINAL_NUMBERS"
  else "SOURCE_DISCREPANCY_REQUIRES_REVIEW"
))
