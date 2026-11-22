#!/usr/bin/env Rscript
# Post-open diagnostic: each of 3 original colonies individually and 2 downstream
# pollen-stage endpoints. This is not a new randomized or paternal-fitness test.
args <- commandArgs(trailingOnly=TRUE)
if (length(args) != 2L)
    stop("Usage: Rscript check_wilkins_2022_colony_and_stigma_stages.R SOURCE_CSV OUT_DIR")
path <- args[[1L]]
out <- args[[2L]]
dir.create(out, recursive=TRUE, showWarnings=FALSE)
suppressPackageStartupMessages(library(digest))
source_sha <- "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62"
if (digest::digest(file=path, algo="sha256") != source_sha)
    stop("Original Wilkins 2022 source hash does not match")
raw <- read.csv(path, na.strings=c("", "NA"), stringsAsFactors=FALSE)
stopifnot(nrow(raw)==60L, !anyDuplicated(raw$BeeID),
          setequal(raw$ColonyID,c("Blue","Orange","Red")),
          setequal(raw$Treatment,c("Cone","Sham")),
          all(raw$BodyPollen==raw$HeadPollen+raw$ThoraxPollen+raw$AbdomenPollen),
          all(raw$PollinatingPollen==raw$BodyPollen+raw$StigmaPollen),
          all(raw$TotalPollen==raw$PollinatingPollen+raw$CorbiculaPollen))
required <- c("HeadWidth","VisitTime","BodyPollen","CorbiculaPollen","StigmaPollen")
d <- raw[complete.cases(raw[required]),,drop=FALSE]
stopifnot(nrow(d)==59L,
          all(d$HeadWidth>0), all(d$VisitTime>0),
          all(d$BodyPollen>0), all(d$CorbiculaPollen>0),
          all(d$StigmaPollen>0))
d$Treatment <- factor(d$Treatment, levels=c("Cone","Sham"))
d$ColonyID <- factor(d$ColonyID, levels=c("Blue","Orange","Red"))
reference_width <- mean(d$HeadWidth)
reference_time <- mean(d$VisitTime)
d$width_centered <- d$HeadWidth - reference_width
d$time_centered <- d$VisitTime - reference_time
# Two different observed stages, one cross-stage composition:
# a stigma deposit is not genotype-verified male fitness.
d$log_body_basket <- log(d$BodyPollen/d$CorbiculaPollen)
d$log_stigma_body <- log(d$StigmaPollen/d$BodyPollen)
d$log_stigma_count <- log(d$StigmaPollen)
responses <- c("log_body_basket","log_stigma_body","log_stigma_count")
formula_for <- function(response,time_adjusted) {
    rhs <- if(time_adjusted) {
        "Treatment*width_centered + time_centered + ColonyID"
    } else {
        "Treatment*width_centered + ColonyID"
    }
    as.formula(paste(response, "~", rhs))
}
key <- "TreatmentSham:width_centered"
# HC3 row-heteroskedastic uncertainty; only 3 colonies, so no cluster-robust
# confidence or p-value is asserted.
hc3_term <- function(fit) {
    design <- model.matrix(fit)
    n <- nrow(design)
    p <- ncol(design)
    if (fit$rank != p || n <= p+2L || !key %in% colnames(design))
        stop("Nonidentified treatment-size contrast")
    h <- hatvalues(fit)
    if (any(!is.finite(h)) || any(h >= .999999))
        stop("Near-perfect leverage prevents HC3 calculation")
    resid <- residuals(fit)
    bread <- solve(crossprod(design))
    meat <- crossprod(design * as.numeric(resid/(1-h)))
    covariance <- bread %*% meat %*% bread
    index <- match(key,colnames(design))
    beta <- unname(coef(fit)[key])
    se <- sqrt(covariance[index,index])
    if (!is.finite(beta) || !is.finite(se) || se<=0)
        stop("Nonfinite treatment-size HC3 estimate")
    halfwidth <- qt(.975,df=n-p)*se
    c(beta=beta,se=se,lo=beta-halfwidth,hi=beta+halfwidth,
      p_approx=2*pt(-abs(beta/se),df=n-p))
}
model_rows <- list()
for (response in responses) {
    for (adjust in c(TRUE,FALSE)) {
        fitted <- lm(formula_for(response,adjust), data=d)
        vals <- hc3_term(fitted)
        label <- if(adjust) "with_postvisit_time" else "without_postvisit_time"
        model_rows[[length(model_rows)+1L]] <- data.frame(
            response=response,adjustment=label,n_bees=nrow(d),
            n_colonies=nlevels(d$ColonyID),
            free_minus_joined_size_beta_per_mm=vals[["beta"]],
            bee_hc3_se=vals[["se"]],
            bee_hc3_lower95=vals[["lo"]],
            bee_hc3_upper95=vals[["hi"]],
            bee_hc3_approximate_p=vals[["p_approx"]],
            coefficient_scale="same response-specific log units",
            not_colony_robust=TRUE,not_male_paternity=TRUE)
    }
}
models <- do.call(rbind,model_rows)
# Exact agreement with the prior, separately fitted equal-bee reduced model is
# an independent source-and-implementation regression gate.
replayed <- subset(models,response=="log_body_basket" &
                   adjustment=="with_postvisit_time")
if (nrow(replayed)!=1L ||
    abs(replayed$free_minus_joined_size_beta_per_mm - 3.17546609)>0.002)
    stop("Incompatible with already verified equal-bee reduced model")
rows <- list()
for (colony in levels(d$ColonyID)) {
    x <- droplevels(d[d$ColonyID==colony,,drop=FALSE])
    n_joined <- sum(x$Treatment=="Cone")
    n_free <- sum(x$Treatment=="Sham")
    if (n_joined < 4L || n_free < 4L)
        stop("Within-colony treated-arm support inadequate")
    support_lo <- max(min(x$HeadWidth[x$Treatment=="Cone"]),
                      min(x$HeadWidth[x$Treatment=="Sham"]))
    support_hi <- min(max(x$HeadWidth[x$Treatment=="Cone"]),
                      max(x$HeadWidth[x$Treatment=="Sham"]))
    overlap <- support_hi > support_lo
    fit <- lm(log_body_basket ~ Treatment*width_centered + time_centered,data=x)
    coefficient <- unname(coef(fit)[key])
    if (fit$rank != ncol(model.matrix(fit)) || !is.finite(coefficient))
        stop("Colony-specific architecture-size coefficient not identifiable")
    se <- summary(fit)$coefficients[key,"Std. Error"]
    df_resid <- df.residual(fit)
    margin <- qt(.975,df_resid)*se
    rows[[length(rows)+1L]] <- data.frame(
        colony=colony,n_bees=nrow(x),n_joined=n_joined,n_free=n_free,
        headwidth_common_support_lo=support_lo,
        headwidth_common_support_hi=support_hi,
        treatment_headwidth_support_overlaps=overlap,
        observed_bees_in_overlap=if(overlap)
           sum(x$HeadWidth>=support_lo & x$HeadWidth<=support_hi) else 0L,
        free_minus_joined_slope_per_mm=coefficient,
        descriptive_ols_se=se,descriptive_ols_lower95=coefficient-margin,
        descriptive_ols_upper95=coefficient+margin,
        valid_population_colony_inference=FALSE)
}
within <- do.call(rbind,rows)
stopifnot(nrow(models)==6L,nrow(within)==3L,
          sum(within$n_bees)==59L)
write.csv(models,file.path(out,"pollen_stage_bee_hc3.csv"),row.names=FALSE)
write.csv(within,file.path(out,"colony_specific_size_slopes.csv"),row.names=FALSE)
write.csv(data.frame(
    source_sha256=source_sha,study_doi="10.1007/s00442-022-05246-0",
    n_complete_bees=59L,n_original_bees=60L,n_colonies=3L,
    source_plant_identity_available=FALSE,bee_headwidth_center=reference_width,
    visit_time_center=reference_time,
    stage_notes=paste("log(stigma/body) is the observed stage inventory ratio,",
                      "not true deposition efficiency or genetic paternity"),
    status="POSTOPEN_EXPLORATORY_WITHIN_COLONY_AND_STIGMA_STAGES",
    not_V4_architecture_adjudication=TRUE,
    treatment_not_assured_random=TRUE,
    post_treatment_visit_time_control=TRUE),
    file.path(out,"colony_stage_inference_scope.csv"),row.names=FALSE)
for(i in seq_len(nrow(within))) {
    x <- within[i,]
    cat(sprintf("WILKINS_COLONY_SPECIFIC|colony=%s|n=%d|joined=%d|free=%d|slope=%+.8f|OLS_CI=[%+.8f,%+.8f]|headwidth_overlap=%s|overlap_bees=%d\n",
                x$colony,x$n_bees,x$n_joined,x$n_free,
                x$free_minus_joined_slope_per_mm,
                x$descriptive_ols_lower95,x$descriptive_ols_upper95,
                tolower(as.character(x$treatment_headwidth_support_overlaps)),
                x$observed_bees_in_overlap))
}
for(i in seq_len(nrow(models))) {
    x <- models[i,]
    cat(sprintf("WILKINS_STIGMA_STAGE|endpoint=%s|spec=%s|n=%d|beta=%+.8f|HC3_CI=[%+.8f,%+.8f]|p=%.8g\n",
                x$response,x$adjustment,x$n_bees,
                x$free_minus_joined_size_beta_per_mm,
                x$bee_hc3_lower95,x$bee_hc3_upper95,
                x$bee_hc3_approximate_p))
}
