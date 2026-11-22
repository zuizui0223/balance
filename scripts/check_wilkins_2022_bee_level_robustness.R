#!/usr/bin/env Rscript
# Post-main-analysis, diagnostic-only bee-level robustness audit.
# The entire 2022 source experiment has 3 colonies: neither individual-grain
# binomial information nor this sensitivity creates independent colony/plant
# replication. This script is deliberately separate from registered main fits.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) {
  stop("Usage: Rscript check_wilkins_2022_bee_level_robustness.R ORIGINAL_CSV OUTPUT_DIR")
}
input <- args[[1]]
out <- args[[2]]
dir.create(out, showWarnings = FALSE, recursive = TRUE)
suppressPackageStartupMessages(library(digest))
expected_digest <- "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62"
if (digest::digest(input, algo = "sha256", file = TRUE) != expected_digest) {
  stop("Wilkins source CSV SHA-256 mismatch. Do not analyze unverified rows.")
}
raw <- read.csv(input, na.strings = c("", "NA"), stringsAsFactors = FALSE)
stopifnot(nrow(raw) == 60L, !anyDuplicated(raw$BeeID),
          identical(sort(unique(raw$ColonyID)), c("Blue", "Orange", "Red")),
          identical(sort(unique(raw$Treatment)), c("Cone", "Sham")))
# The original model used 59 complete bees due to one missing head width.
d <- droplevels(raw[complete.cases(raw[, c("HeadWidth", "VisitTime",
                                          "BodyPollen", "CorbiculaPollen")]), ])
stopifnot(nrow(d) == 59L, length(unique(d$BeeID)) == 59L,
          all(is.finite(d$HeadWidth)), all(d$HeadWidth > 0),
          all(is.finite(d$VisitTime)), all(d$VisitTime > 0),
          all(d$BodyPollen > 0), all(d$CorbiculaPollen > 0),
          all(d$BodyPollen == d$HeadPollen+d$ThoraxPollen+d$AbdomenPollen))
# One observation is one bee, regardless of the number of pollen grains.
d$Treatment <- factor(d$Treatment, levels = c("Cone", "Sham"))
d$ColonyID <- factor(d$ColonyID)
fixed_width <- mean(d$HeadWidth)
fixed_time <- mean(d$VisitTime)
d$width_centered <- d$HeadWidth - fixed_width
d$time_centered <- d$VisitTime - fixed_time
d$log_body_vs_basket <- log(d$BodyPollen / d$CorbiculaPollen)
# Fixed before the sensitivity results: original full three-way hierarchy and
# one simpler reduced two-way specification. No model selected by significance.
specs <- list(
  full_three_way = log_body_vs_basket ~ Treatment * width_centered *
    time_centered + ColonyID,
  reduced_two_way = log_body_vs_basket ~ Treatment * width_centered +
    time_centered + ColonyID
)
key <- "TreatmentSham:width_centered"

# HC3 is computed on the 59 BEE rows. It is not a reliable colony-robust SE
# with only three independent colony groups, or a randomization p value.
single_fit <- function(subset, form, model, dropped_colony = "none") {
  subset <- droplevels(subset)
  fit <- lm(form, data = subset)
  X <- model.matrix(fit)
  n <- nrow(X)
  p <- ncol(X)
  if (fit$rank != p || n <= p+2L || !(key %in% colnames(X))) {
    stop(paste("Rank or support failure in", model, dropped_colony))
  }
  h <- hatvalues(fit)
  if (any(!is.finite(h)) || any(h > 0.9999999)) {
    stop("Near-perfect leverage invalidates HC3 sensitivity")
  }
  e <- residuals(fit)
  inverse <- solve(crossprod(X))
  meat <- crossprod(X * as.numeric(e/(1-h)))
  covariance <- inverse %*% meat %*% inverse
  robust_se <- sqrt(diag(covariance)[match(key, colnames(X))])
  beta <- unname(coef(fit)[key])
  df <- n-p
  if (!is.finite(robust_se) || robust_se <= 0 || !is.finite(beta)) {
    stop("Nonfinite bee-level HC3 sensitivity estimate")
  }
  margin <- qt(0.975, df) * robust_se
  data.frame(
    specification=model, dropped_colony=dropped_colony,
    n_bees=n, n_colonies=length(unique(subset$ColonyID)),
    model_columns=p, beta_free_minus_joined_per_mm=beta,
    hc3_se=robust_se, lower95=beta-margin, upper95=beta+margin,
    approximate_t_p=2*pt(-abs(beta/robust_se), df=df),
    max_leverage=max(h), n_high_leverage=sum(h > 2*p/n),
    stringsAsFactors=FALSE
  )
}
full <- do.call(rbind, lapply(names(specs), function(label) {
  single_fit(d, specs[[label]], label)
}))
colony_deleted <- do.call(rbind, unlist(lapply(names(specs), function(label) {
  lapply(levels(d$ColonyID), function(colony) {
    single_fit(d[d$ColonyID != colony, , drop=FALSE], specs[[label]],
               label, dropped_colony=colony)
  })
}), recursive=FALSE))
bee_deleted <- do.call(rbind, unlist(lapply(names(specs), function(label) {
  lapply(seq_len(nrow(d)), function(index) {
    single_fit(d[-index, , drop=FALSE], specs[[label]], label,
               dropped_colony="one_bee_not_identified")
  })
}), recursive=FALSE))
summaries <- do.call(rbind, lapply(split(bee_deleted, bee_deleted$specification),
  function(group) {
    reference <- full[full$specification == group$specification[1], ]
    colony_group <- subset(colony_deleted, specification == group$specification[1])
    data.frame(
      specification=group$specification[1], n_bee_deletions=nrow(group),
      n_colony_deletions=nrow(colony_group),
      original_sign=sign(reference$beta_free_minus_joined_per_mm),
      n_bee_deletions_preserving_sign=sum(
        sign(group$beta_free_minus_joined_per_mm)==sign(reference$beta_free_minus_joined_per_mm)),
      n_colony_deletions_preserving_sign=sum(
        sign(colony_group$beta_free_minus_joined_per_mm)==sign(reference$beta_free_minus_joined_per_mm)),
      bee_deleted_beta_min=min(group$beta_free_minus_joined_per_mm),
      bee_deleted_beta_max=max(group$beta_free_minus_joined_per_mm),
      colony_deleted_beta_min=min(colony_group$beta_free_minus_joined_per_mm),
      colony_deleted_beta_max=max(colony_group$beta_free_minus_joined_per_mm),
      n_bee_deletions_hc3_ci_excluding_zero=sum(
        group$lower95>0 | group$upper95<0),
      n_colony_deletions_hc3_ci_excluding_zero=sum(
        colony_group$lower95>0 | colony_group$upper95<0)
    )
  }))
stopifnot(nrow(full)==2L, nrow(colony_deleted)==6L,
          nrow(bee_deleted)==118L, nrow(summaries)==2L,
          all(full$n_bees == 59L), all(full$n_colonies==3L))
write.csv(full, file.path(out, "bee_level_hc3_contrasts.csv"), row.names=FALSE)
write.csv(colony_deleted, file.path(out,"leave_one_colony_out.csv"), row.names=FALSE)
write.csv(summaries, file.path(out,"leave_one_bee_out_summary.csv"), row.names=FALSE)
write.csv(data.frame(source_sha256=expected_digest,
   one_row_per_bee=TRUE, n_complete_bees=nrow(d), n_colonies=3L,
   centered_headwidth_mm=fixed_width, centered_visit_seconds=fixed_time,
   outcome="log(BodyPollen/CorbiculaPollen)",
   analysis_status="POSTOPEN_BEE_LEVEL_SENSITIVITY_NOT_CONFIRMATORY",
   no_colony_robust_p_value=TRUE, no_genetic_paternity=TRUE),
   file.path(out,"bee_level_scope.csv"), row.names=FALSE)
for (i in seq_len(nrow(full))) {
  a <- full[i,]
  s <- summaries[summaries$specification==a$specification,]
  cat(sprintf(
    "BALANCE_WILKINS_BEE_SENSITIVITY|model=%s|n=%d|beta=%+.8f|hc3_se=%.8f|p=%.8g|CI=[%+.8f,%+.8f]|bee_sign=%d/%d|colony_sign=%d/%d|colony_beta=[%+.8f,%+.8f]\n",
    a$specification,a$n_bees,a$beta_free_minus_joined_per_mm,a$hc3_se,
    a$approximate_t_p,a$lower95,a$upper95,
    s$n_bee_deletions_preserving_sign,s$n_bee_deletions,
    s$n_colony_deletions_preserving_sign,s$n_colony_deletions,
    s$colony_deleted_beta_min,s$colony_deleted_beta_max
  ))
}
