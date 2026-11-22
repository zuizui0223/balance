#!/usr/bin/env Rscript
# Post-open, paired three-destination analysis of authentic Wilkins 2022 source.
# A difference of p-values is not a test of a difference in stage effects.
# Instead estimate the source-architecture×bee-width contrast jointly on
# terminal-body/basket and deposited-stigma/terminal-body log ratios.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) {
  stop("Usage: Rscript check_wilkins_2022_paired_stage_contrasts.R VERIFIED_CSV OUT_DIR")
}
source_file <- args[[1]]
out_dir <- args[[2]]
dir.create(out_dir, recursive=TRUE, showWarnings=FALSE)
suppressPackageStartupMessages(library(digest))
source_sha <- "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62"
if (digest::digest(source_file, algo="sha256", file=TRUE) != source_sha) {
  stop("Original Wilkins source bytes mismatch")
}
dat <- read.csv(source_file, na.strings=c("", "NA"), stringsAsFactors=FALSE)
stopifnot(nrow(dat) == 60L, !anyDuplicated(dat$BeeID),
          setequal(dat$ColonyID, c("Blue", "Orange", "Red")),
          setequal(dat$Treatment, c("Cone", "Sham")),
          all(dat$BodyPollen == dat$HeadPollen+dat$ThoraxPollen+dat$AbdomenPollen),
          all(dat$PollinatingPollen == dat$BodyPollen+dat$StigmaPollen))
required <- c("HeadWidth", "VisitTime", "BodyPollen", "CorbiculaPollen", "StigmaPollen")
d <- dat[complete.cases(dat[,required]),,drop=FALSE]
stopifnot(nrow(d)==59L,
          all(d$HeadWidth>0), all(d$VisitTime>0),
          all(d$BodyPollen>0), all(d$CorbiculaPollen>0),
          all(d$StigmaPollen>0))
d$Treatment <- factor(d$Treatment,levels=c("Cone","Sham"))
d$ColonyID <- factor(d$ColonyID,levels=c("Blue","Orange","Red"))
d$width_centered <- d$HeadWidth-mean(d$HeadWidth)
d$time_centered <- d$VisitTime-mean(d$VisitTime)
d$body_basket <- log(d$BodyPollen/d$CorbiculaPollen)
d$stigma_body <- log(d$StigmaPollen/d$BodyPollen)
d$stigma_basket <- log(d$StigmaPollen/d$CorbiculaPollen)
if (max(abs(d$body_basket+d$stigma_body-d$stigma_basket))>1e-12) {
  stop("Within-bee pollen stage identity violated")
}
# Set independent response basis before viewing any regression output.
# Both outcomes are on log-ratio scale; preserve the within-bee covariance.
responses <- cbind(body_basket=d$body_basket,stigma_body=d$stigma_body)
specifications <- list(
  with_postvisit_time = ~ Treatment*width_centered+time_centered+ColonyID,
  without_postvisit_time = ~ Treatment*width_centered+ColonyID
)
key <- "TreatmentSham:width_centered"

joint_fit <- function(name, spec) {
  X <- model.matrix(spec, data=d)
  n <- nrow(X); p <- ncol(X)
  if (n!=59L || qr(X)$rank!=p || n<=p+2L || !(key %in% colnames(X))) {
    stop("Source paired-stage design rank or support failure")
  }
  inverse <- solve(crossprod(X))
  beta <- inverse%*%crossprod(X,responses)
  residual <- responses-X%*%beta
  h <- rowSums((X%*%inverse)*X)
  if (any(!is.finite(h)) || any(h >= .999999)) {
    stop("HC3 cannot handle near-perfect source bee leverage")
  }
  k <- match(key,colnames(X))
  bee_multiplier <- as.numeric((X%*%inverse)[,k])/(1-h)
  # Each bee contributes a two-component score, including covariance between
  # paired pollen responses; no pollen-grain pseudo-replication.
  scores <- residual*bee_multiplier
  V <- crossprod(scores)
  if (!all(is.finite(V)) || any(!is.finite(beta))) {
    stop("Paired source HC3 covariance nonfinite")
  }
  chol(V) # two independent stage contrasts must have stable covariance
  b <- as.numeric(beta[k,])
  names(b) <- colnames(responses)
  # Stigma/basket=body/basket+stigma/body at each bee. Same design implies
  # the coefficient and covariance identity EXACTLY, no joint p-value shortcut.
  transforms <- rbind(
    body_vs_basket=c(1,0),
    stigma_vs_body=c(0,1),
    stigma_vs_basket=c(1,1),
    difference_body_vs_basket_minus_stigma_vs_basket=c(0,-1)
  )
  out <- do.call(rbind, lapply(rownames(transforms),function(endpoint) {
    w <- transforms[endpoint,]
    estimate <- sum(w*b)
    se <- sqrt(drop(t(w)%*%V%*%w))
    if (!is.finite(se) || se<=0) stop("Nonfinite stage HC3 standard error")
    half <- qt(.975,df=n-p)*se
    data.frame(
      specification=name,contrast=endpoint,
      n_bees=n,n_colonies=3L,n_model_columns=p,
      beta_free_minus_joined_headwidth_per_mm=estimate,
      bee_hc3_se=se,bee_hc3_lower95=estimate-half,
      bee_hc3_upper95=estimate+half,
      bee_hc3_approximate_p=2*pt(-abs(estimate/se),df=n-p),
      not_colony_robust=TRUE,not_genetic_paternity=TRUE,
      stringsAsFactors=FALSE
    )
  }))
  # Omnibus tests whether the 3 destination-specific treatment×width slopes
  # have the same value, i.e. the two independent differences are both zero.
  statistic <- drop(t(b)%*%solve(V,b))
  if (!is.finite(statistic) || statistic<0) {
    stop("Invalid paired contrast Wald statistic")
  }
  omnibus <- data.frame(
    specification=name,n_bees=n,n_colonies=3L,
    test="equal_architecture_by_width_slopes_for_log_body_log_basket_log_stigma",
    wald_chisquare_2df=statistic,asymptotic_chisquare_p=pchisq(statistic,df=2,lower.tail=FALSE),
    claim="EXPLORATORY_BEE_HC3_OMNIBUS_NOT_THREE_INDEPENDENT_STUDIES",
    stringsAsFactors=FALSE
  )
  list(rows=out,omnibus=omnibus,covariance=V)
}
result <- lapply(names(specifications),function(x)joint_fit(x,specifications[[x]]))
names(result)<-names(specifications)
all_rows <- do.call(rbind,lapply(result,\`[[\`,"rows"))
all_omnibus <- do.call(rbind,lapply(result,\`[[\`,"omnibus"))
# Two independent regression implementations should reproduce the already
# archived same-bee stage model, including the direct formal difference test.
adjusted <- subset(all_rows,specification=="with_postvisit_time")
body <- subset(adjusted,contrast=="body_vs_basket")
stigma_body <- subset(adjusted,contrast=="stigma_vs_body")
if (abs(body$beta_free_minus_joined_headwidth_per_mm-3.17546609)>0.002 ||
    abs(stigma_body$beta_free_minus_joined_headwidth_per_mm+2.78571840)>0.002 ||
    abs(body$bee_hc3_lower95-.95490686)>.002 ||
    abs(stigma_body$bee_hc3_upper95-2.94738417)>.002) {
  stop("Paired joint-stage model disagrees with independently verified previous source analysis")
}
write.csv(all_rows,file.path(out_dir,"paired_stage_effect_contrasts.csv"),row.names=FALSE)
write.csv(all_omnibus,file.path(out_dir,"paired_stage_omnibus.csv"),row.names=FALSE)
write.csv(data.frame(
  source_sha256=source_sha,n_observed_bees=59L,n_colonies=3L,
  same_bee_paired_covariance=TRUE,no_independent_pollen_grain_replication=TRUE,
  treatment="Cone joined vs Sham free (alternating, not assured randomized)",
  estimand="free-minus-joined headwidth slope difference; conditional within original study",
  direct_difference="beta(body/basket)-beta(stigma/basket)=beta(body/stigma)",
  no_measured_male_genetic_paternity=TRUE,
  no_plant_fitness=TRUE,
  exploratory_postopen=TRUE,
  no_colony_robust_p_values=TRUE),
  file.path(out_dir,"paired_stage_inference_scope.csv"),row.names=FALSE
)
for(i in seq_len(nrow(all_rows))) {
  z<-all_rows[i,]
  cat(sprintf("WILKINS_PAIRED_STAGE|spec=%s|contrast=%s|n=%d|beta=%+.8f|HC3_CI=[%+.8f,%+.8f]|p=%.8g\\n",
    z$specification,z$contrast,z$n_bees,
    z$beta_free_minus_joined_headwidth_per_mm,
    z$bee_hc3_lower95,z$bee_hc3_upper95,z$bee_hc3_approximate_p))
}
for(i in seq_len(nrow(all_omnibus))) {
  z<-all_omnibus[i,]
  cat(sprintf("WILKINS_PAIRED_OMNIBUS|spec=%s|Wald2=%.8f|p=%.8g\\n",
              z$specification,z$wald_chisquare_2df,z$asymptotic_chisquare_p))
}
