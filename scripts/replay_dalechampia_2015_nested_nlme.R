#!/usr/bin/env Rscript
# Source-authenticated posthoc random-effect comparison for 2015 Dalechampia.
# Entire-blossom foil cover, NOT selective bract photosynthesis manipulation.
# This is a sensitivity test of experimental-unit dependence, not the source
# authors' published model or proof that their mixed-model inference is wrong.
args <- commandArgs(trailingOnly=TRUE)
if (length(args)!=3L) stop("usage: replay_dalechampia_2015_nested_nlme.R original_seeds.txt covariance_models.csv treatment_effects.csv")
if (!requireNamespace("nlme",quietly=TRUE)) stop("R nlme package needed")
seed_file <- args[1]
models_csv <- args[2]
coefficients_csv <- args[3]
if (file.info(seed_file)$size != 84562 ||
    unname(tools::md5sum(seed_file)) != "0d64b8a35835bfd23e0feab9276026bb") {
  stop("original Pélabon et al. archived source bytes do not match published Dryad")
}
d <- read.table(seed_file,header=TRUE,sep="\t",dec=",",quote="",
                fileEncoding="latin1",stringsAsFactors=FALSE,na.strings=c("NA",""))
if (nrow(d)!=1221L || sum(is.na(d$seedmass))!=1L ||
    sum(d$seedmass < 20, na.rm=TRUE)!=117L) {
  stop("original 2015 raw source count/abortion-proxy format changed")
}
d <- subset(d,!is.na(seedmass) & seedmass>=20)
d$FemaleID <- factor(as.character(d$FemaleID))
d$crossID <- factor(as.character(d$crossID))
d$treatcode <- factor(d$treatcode,levels=c("cont","bag","cut","cutcont"))
blossom <- interaction(d$FemaleID,d$crossID,drop=TRUE)
if (nrow(d)!=1103L || nlevels(d$FemaleID)!=36L ||
    nlevels(blossom)!=132L ||
    anyNA(d[,c("ped","seedmass","treatcode")])) {
  stop("source treatment units or mother/blossom dependence changed")
}

formula <- seedmass ~ ped + treatcode
control <- nlme::lmeControl(opt="optim",msMaxIter=300,niterEM=40,
                            returnObject=FALSE)
# Both models fit exactly the same 1103 original measured seeds and same
# fixed effects, changing ONLY the random-effect covariance decomposition.
fitmodel <- function(nested,method) {
  grouping <- if (nested) ~1|FemaleID/crossID else ~1|FemaleID
  nlme::lme(fixed=formula,random=grouping,data=d,
            method=method,na.action=na.fail,control=control)
}
ml_m <- fitmodel(FALSE,"ML")
ml_mb <- fitmodel(TRUE,"ML")
reml_m <- fitmodel(FALSE,"REML")
reml_mb <- fitmodel(TRUE,"REML")

get_variances <- function(fit,nested) {
  tbl <- nlme::VarCorr(fit)
  values <- suppressWarnings(as.numeric(tbl[,"Variance"]))
  values <- values[is.finite(values)]
  expected <- if (nested) 3L else 2L
  if (length(values) != expected || any(values<=0))
    stop("source random-effect covariance decomposition changed")
  if (nested) c(mother=values[1],blossom=values[2],residual=values[3])
  else c(mother=values[1],blossom=0,residual=values[2])
}
fits=list(maternal_only=list(ml=ml_m,reml=reml_m,nested=FALSE),
          maternal_plus_blossom=list(ml=ml_mb,reml=reml_mb,nested=TRUE))
rows=list()
effects=list()
for (id in names(fits)) {
  fit=fits[[id]]
  variances=get_variances(fit$ml,fit$nested)
  total=sum(variances)
  if (!is.finite(total) || total<=0) stop("nonfinite random-effect variance")
  rows[[id]]=data.frame(
    model_id=id,n_seeds=nrow(d),n_blossoms=nlevels(blossom),
    n_mothers=nlevels(d$FemaleID),
    ml_aic=as.numeric(AIC(fit$ml)),
    ml_loglik=as.numeric(logLik(fit$ml)),
    mother_variance=unname(variances["mother"]),
    blossom_variance=unname(variances["blossom"]),
    residual_variance=unname(variances["residual"]),
    implied_same_blossom_seed_correlation=unname(
      (variances["mother"]+variances["blossom"])/total
    ),
    implied_same_mother_different_blossom_seed_correlation=unname(
      variances["mother"]/total
    ),
    stringsAsFactors=FALSE
  )
  tt=summary(fit$reml)$tTable
  for (term in c("treatcodebag","treatcodecut","treatcodecutcont","ped")) {
    if (!(term %in% rownames(tt))) stop("registered fixed treatment term missing")
    effects[[paste(id,term,sep="::")]]=data.frame(
      model_id=id,term=term,
      reml_beta=unname(tt[term,"Value"]),
      reml_se=unname(tt[term,"Std.Error"]),
      normal_wald95_lo=unname(tt[term,"Value"])-1.96*unname(tt[term,"Std.Error"]),
      normal_wald95_hi=unname(tt[term,"Value"])+1.96*unname(tt[term,"Std.Error"]),
      stringsAsFactors=FALSE
    )
  }
}
write.csv(do.call(rbind,rows),models_csv,row.names=FALSE,quote=TRUE)
write.csv(do.call(rbind,effects),coefficients_csv,row.names=FALSE,quote=TRUE)
cat("Original source seeds",nrow(d),"blossoms",nlevels(blossom),
    "mothers",nlevels(d$FemaleID),"\n")
cat("Maternal-only AIC",rows[["maternal_only"]]$ml_aic,"\n")
cat("Maternal-and-blossom AIC",rows[["maternal_plus_blossom"]]$ml_aic,"\n")
cat("Nested seed-same-blossom ICC",
    rows[["maternal_plus_blossom"]]$implied_same_blossom_seed_correlation,"\n")
cat("Original source 2015 nlme model NOT claimed reproduced; this is a posthoc experimental-unit covariance audit.\n")
