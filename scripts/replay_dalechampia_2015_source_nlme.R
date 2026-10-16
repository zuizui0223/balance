#!/usr/bin/env Rscript
# Independent exact-source audit using the paper's stated R nlme family.
#
# Original Pélabon et al. (2015) Table 2: plant random intercept; ML AIC model
# comparison, REML fixed-effect estimates. This is a best-effort registered
# reconstruction, NOT the authors' recovered R script or the 2015 R package.
#
# Reads original Dryad CC0 text only after external size/MD5 preflight.
# Never guesses missing raw observations, infers embryo morphology, or promotes
# "bag" (whole-blossom foil) to selective bract photosynthetic manipulation.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 3L) {
  stop("usage: replay_dalechampia_2015_source_nlme.R seed_original.txt models.csv fixed_effects.csv")
}
if (!requireNamespace("nlme", quietly = TRUE)) {
  stop("nlme package is required, cannot replace it with alternative inference")
}
input <- args[1]
models_output <- args[2]
effects_output <- args[3]

expected_bytes <- 84562
expected_md5 <- "0d64b8a35835bfd23e0feab9276026bb"
if (is.na(file.info(input)$size) ||
    file.info(input)$size != expected_bytes ||
    unname(tools::md5sum(input)) != expected_md5) {
  stop("original seed file byte count / MD5 differs from published Dryad")
}

df <- read.table(input,
                 header = TRUE, sep = "\t", dec = ",", quote = "",
                 fileEncoding = "latin1", stringsAsFactors = FALSE,
                 na.strings = c("NA", ""), check.names = TRUE)
if (nrow(df) != 1221 || sum(is.na(df$seedmass)) != 1L ||
    sum(df$seedmass < 20, na.rm = TRUE) != 117L) {
  stop("original Dryad seed mass sample support changed")
}
df <- subset(df, !is.na(seedmass) & seedmass >= 20)
df$FemaleID <- factor(as.character(df$FemaleID))
df$treatcode <- factor(df$treatcode, levels = c("cont", "bag", "cut", "cutcont"))
if (nrow(df) != 1103 || nlevels(df$FemaleID) != 36 ||
    length(unique(paste(df$FemaleID, df$crossID, sep = "::"))) != 132) {
  stop("original seed mass model unit count changed")
}
if (anyNA(df[, c("FemaleID","seedmass","treatcode","ped","seedset")])) {
  stop("registered source model data contain missing covariates")
}

formulas <- list(
  ped_seedset_treat = seedmass ~ ped + seedset + treatcode,
  ped_treat = seedmass ~ ped + treatcode,
  ped_seedset = seedmass ~ ped + seedset,
  seedset_only = seedmass ~ seedset,
  ped_only = seedmass ~ ped,
  intercept = seedmass ~ 1
)
candidate_order <- names(formulas)
model_rows <- list()
fixed_rows <- list()

# Explicit model fit status. If a solver cannot converge, fail the source
# route rather than silently replacing nlme or deleting observations.
for (id in candidate_order) {
  fixed_formula <- formulas[[id]]
  ml <- nlme::lme(
    fixed = fixed_formula, random = ~1 | FemaleID,
    data = df, method = "ML", na.action = na.fail,
    control = nlme::lmeControl(
      opt = "optim", msMaxIter = 300, niterEM = 40, returnObject = FALSE
    )
  )
  reml <- update(ml, method = "REML")
  if (ml$dims$N != nrow(df) || reml$dims$N != nrow(df)) {
    stop("lme silently changed source analysis row count")
  }
  table_ml <- summary(ml)$tTable
  table_reml <- summary(reml)$tTable

  model_rows[[id]] <- data.frame(
    model_id = id,
    n_obs = nrow(df),
    n_mothers = nlevels(df$FemaleID),
    ml_loglik = as.numeric(logLik(ml)),
    ml_aic = as.numeric(AIC(ml)),
    ml_bic = as.numeric(BIC(ml)),
    ml_residual_sd = as.numeric(ml$sigma),
    reml_residual_sd = as.numeric(reml$sigma),
    stringsAsFactors = FALSE
  )
  for (coefficient in rownames(table_reml)) {
    fixed_rows[[paste(id,coefficient,sep="::")]] <- data.frame(
      model_id = id,
      term = coefficient,
      ml_point = unname(nlme::fixef(ml)[coefficient]),
      reml_point = unname(table_reml[coefficient, "Value"]),
      reml_se = unname(table_reml[coefficient, "Std.Error"]),
      stringsAsFactors = FALSE
    )
  }
}
# This variance sensitivity is a separate experiment-level model;
# do not confuse it with original source Table 2 AIC candidates.
varident <- nlme::lme(
  fixed = formulas[["ped_treat"]], random = ~1 | FemaleID,
  data = df, method = "ML", na.action = na.fail,
  weights = nlme::varIdent(form = ~1 | treatcode),
  control = nlme::lmeControl(
    opt = "optim", msMaxIter = 300, niterEM = 40, returnObject = FALSE
  )
)
model_rows[["ped_treat__heterogeneous_residual"]] <- data.frame(
  model_id = "ped_treat__heterogeneous_residual",
  n_obs = nrow(df), n_mothers = nlevels(df$FemaleID),
  ml_loglik = as.numeric(logLik(varident)),
  ml_aic = as.numeric(AIC(varident)),
  ml_bic = as.numeric(BIC(varident)),
  ml_residual_sd = as.numeric(varident$sigma),
  reml_residual_sd = NA_real_,
  stringsAsFactors = FALSE
)

write.csv(do.call(rbind, model_rows), file=models_output,
          row.names=FALSE, quote=TRUE, na="")
write.csv(do.call(rbind, fixed_rows), file=effects_output,
          row.names=FALSE, quote=TRUE, na="")
cat("Dalechampia exact source n =", nrow(df), "mothers =", nlevels(df$FemaleID),
    "nlme package version =", as.character(utils::packageVersion("nlme")), "\n")
for (id in candidate_order) {
  cat(id, "ML AIC =", model_rows[[id]]$ml_aic, "\n")
}
cat("heterogeneous residual AIC =",
    model_rows[["ped_treat__heterogeneous_residual"]]$ml_aic, "\n")
