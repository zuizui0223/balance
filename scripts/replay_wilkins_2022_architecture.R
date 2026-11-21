#!/usr/bin/env Rscript
# Fixed replay of the five author models and two endpoint-definition sensitivities.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Usage: Rscript replay_wilkins_2022_architecture.R VERIFIED_CSV OUT_DIR")
source_path <- args[[1]]
out_dir <- args[[2]]
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
suppressPackageStartupMessages(library(glmmTMB))
suppressPackageStartupMessages(library(car))
writeLines(c(capture.output(sessionInfo()), paste("glmmTMB", packageVersion("glmmTMB")),
             paste("car", packageVersion("car")), paste("TMB", packageVersion("TMB"))),
           file.path(out_dir, "session_info.txt"))

# Enforce the data check even when the script is invoked without the workflow.
digest <- digest::digest(file = source_path, algo = "sha256")
if (digest != "0d433ba471cc7c1cbcdc3ce4bf0fd8a599b04176b4e85c7425ab67fad6703c62")
    stop("CSV does not match the authenticated publisher supplement")
bees <- read.csv(source_path, na.strings = c("", "NA"), stringsAsFactors = FALSE)
bees$Treatment <- factor(bees$Treatment, levels = c("Cone", "Sham"))
bees$ColonyID <- factor(bees$ColonyID)
bees$BeeID <- factor(bees$BeeID)
options(contrasts = c("contr.treatment", "contr.poly"))
stopifnot(nrow(bees) == 60L, !anyDuplicated(bees$BeeID), !anyNA(bees$Treatment),
          all(bees$BodyPollen == bees$HeadPollen + bees$ThoraxPollen + bees$AbdomenPollen),
          all(bees$PollinatingPollen == bees$BodyPollen + bees$StigmaPollen),
          all(bees$TotalPollen == bees$PollinatingPollen + bees$CorbiculaPollen))

formulas <- list(
    anther_remaining = log(AntherPollen) ~ Treatment * HeadWidth * VisitTime + (1|ColonyID),
    basket = log(CorbiculaPollen) ~ Treatment * VisitTime * HeadWidth + (1|ColonyID),
    published_composite = log(PollinatingPollen) ~ Treatment * HeadWidth * VisitTime + (1|ColonyID),
    published_share = cbind(PollinatingPollen, TotalPollen - PollinatingPollen) ~
        Treatment * HeadWidth * VisitTime + (1|ColonyID/BeeID),
    stigma = log(StigmaPollen) ~ Treatment * log(BodyPollen) +
        Treatment * VisitTime * HeadWidth + (1|ColonyID),
    body_only = log(BodyPollen) ~ Treatment * HeadWidth * VisitTime + (1|ColonyID),
    body_only_share = cbind(BodyPollen, CorbiculaPollen) ~
        Treatment * HeadWidth * VisitTime + (1|ColonyID/BeeID)
)
# Type II chi squares in the authors' archived R comments (supplement 2).
size_first <- c("Treatment", "HeadWidth", "VisitTime", "Treatment:HeadWidth",
                "Treatment:VisitTime", "HeadWidth:VisitTime", "Treatment:HeadWidth:VisitTime")
time_first <- c("Treatment", "VisitTime", "HeadWidth", "Treatment:VisitTime",
                "Treatment:HeadWidth", "VisitTime:HeadWidth", "Treatment:VisitTime:HeadWidth")
stigma_terms <- c("Treatment", "log(BodyPollen)", "VisitTime", "HeadWidth",
                  "Treatment:log(BodyPollen)", "Treatment:VisitTime", "Treatment:HeadWidth",
                  "VisitTime:HeadWidth", "Treatment:VisitTime:HeadWidth")
published <- list(
    anther_remaining = setNames(c(12.1344, .5479, .0208, .3261, 1.9808, 1.7787, .0001), size_first),
    basket = setNames(c(4.1111, .1021, 7.4348, .4784, 4.7248, .0153, 2.2801), time_first),
    published_composite = setNames(c(5.6139, .4505, 3.3428, 4.1480, .2806, 1.6085, .5523), size_first),
    published_share = setNames(c(.0000, 3.9486, 1.3287, 13.1120, .0482, .7921, .6493), size_first),
    stigma = setNames(c(.4142, .1458, 1.9305, 4.8341, 5.2986, .0072, .4723, 1.0955, .0014), stigma_terms)
)
share_models <- c("published_share", "body_only_share")

# Common conditional contrast grid: range intersection, then pooled type-7 quantiles.
by_arm <- split(bees$HeadWidth, bees$Treatment)
support_low <- max(vapply(by_arm, min, numeric(1), na.rm = TRUE))
support_high <- min(vapply(by_arm, max, numeric(1), na.rm = TRUE))
width <- with(bees, HeadWidth[!is.na(HeadWidth) & HeadWidth >= support_low & HeadWidth <= support_high])
probe_widths <- unname(quantile(width, c(.25, .75), type = 7))
probe_time <- mean(bees$VisitTime)
probe_body <- median(bees$BodyPollen)
write.csv(data.frame(width_min = support_low, width_max = support_high, n_overlap = length(width),
                     quantile_type = 7, head_width_p25 = probe_widths[1], head_width_p75 = probe_widths[2],
                     pooled_mean_visit_time = probe_time, pooled_median_body_pollen = probe_body,
                     pooled_n = nrow(bees)), file.path(out_dir, "contrast_grid.csv"), row.names = FALSE)

wald_contrast <- function(model, label, fit, weights, width, scale) {
    beta <- fixef(fit)$cond
    cov <- vcov(fit)$cond
    weights <- weights[names(beta)]
    estimate <- sum(weights * beta)
    se <- sqrt(drop(t(weights) %*% cov[names(beta), names(beta)] %*% weights))
    stopifnot(is.finite(se), se > 0, is.finite(estimate))
    margin <- qnorm(.975) * se
    data.frame(model, contrast = label, scale, head_width = width, visit_time = probe_time,
               body_pollen = if (model == "stigma") probe_body else NA_real_,
               estimate, se, lower_95 = estimate - margin, upper_95 = estimate + margin)
}

fit_contrasts <- function(model, fit) {
    beta <- fixef(fit)$cond
    fixed_terms <- delete.response(terms(lme4::nobars(formulas[[model]])))
    rows <- list()
    for (i in seq_along(probe_widths)) {
        probe <- data.frame(Treatment = factor(c("Cone", "Sham"), levels = levels(bees$Treatment)),
                            VisitTime = probe_time, HeadWidth = probe_widths[i], BodyPollen = probe_body)
        design <- model.matrix(fixed_terms, probe)
        rows[[i]] <- wald_contrast(model, paste0("free_minus_joined_width_p", c(25, 75)[i]),
                                  fit, design[2, ] - design[1, ], probe_widths[i],
                                  if (model %in% share_models) "log_odds" else "log_grains")
    }
    if (model == "stigma") {
        joined <- setNames(numeric(length(beta)), names(beta))
        joined["log(BodyPollen)"] <- 1
        interaction <- "TreatmentSham:log(BodyPollen)"
        stopifnot(interaction %in% names(beta))
        free <- joined
        free[interaction] <- 1
        slopes <- list(joined_log_body_slope = joined, free_log_body_slope = free,
                       free_minus_joined_log_body_slope = free - joined)
        for (label in names(slopes)) {
            rows[[length(rows) + 1L]] <- wald_contrast(model, label, fit, slopes[[label]], NA_real_,
                                                      "log_grains_per_log_body_grain")
        }
    }
    do.call(rbind, rows)
}

diagnostics <- list()
tests <- list()
coefficients <- list()
contrasts <- list()
for (model in names(formulas)) {
    warnings_seen <- character()
    model_formula <- formulas[[model]]
    expected_n <- sum(complete.cases(bees[all.vars(model_formula)]))
    diag_row <- data.frame(model, source_sha256 = digest,
                           family = if (model %in% share_models) "binomial" else "gaussian",
                           formula = paste(deparse(model_formula), collapse = " "),
                           expected_n, n = NA_integer_, convergence = NA_integer_,
                           positive_definite_hessian = NA, max_abs_fixed_gradient = NA_real_,
                           colony_variance = NA_real_, bee_within_colony_variance = NA_real_,
                           optimizer_message = "", warnings = "", error = "", usable = FALSE)
    tryCatch(withCallingHandlers({
        family <- if (model %in% share_models) binomial() else gaussian()
        fit <- glmmTMB(model_formula, data = bees, family = family, REML = FALSE,
                       na.action = na.omit)
        diag_row$n <- nobs(fit)
        diag_row$convergence <- fit$fit$convergence
        diag_row$positive_definite_hessian <- isTRUE(fit$sdr$pdHess)
        if (length(fit$sdr$gradient.fixed))
            diag_row$max_abs_fixed_gradient <- max(abs(fit$sdr$gradient.fixed))
        diag_row$optimizer_message <- paste(fit$fit$message, collapse = "; ")
        v <- VarCorr(fit)$cond
        diag_row$colony_variance <- unname(v[["ColonyID"]][1, 1])
        if (model %in% share_models) {
            nested <- setdiff(names(v), "ColonyID")
            stopifnot(length(nested) == 1L)
            diag_row$bee_within_colony_variance <- unname(v[[nested]][1, 1])
        }
        if (diag_row$n != expected_n || diag_row$convergence != 0L || !diag_row$positive_definite_hessian)
            stop("Model failed the sample count, convergence, or Hessian check")
        coef_mat <- summary(fit)$coefficients$cond
        stopifnot(all(is.finite(coef_mat)))
        co <- data.frame(model, term = rownames(coef_mat), estimate = coef_mat[, 1],
                         se = coef_mat[, 2], z = coef_mat[, 3], p = coef_mat[, 4], row.names = NULL)
        test <- as.data.frame(car::Anova(fit, type = 2))
        tab <- data.frame(model, term = rownames(test), chisq = test[["Chisq"]],
                          df = test[["Df"]], p = test[["Pr(>Chisq)"]], source_chisq = NA_real_,
                          delta_chisq = NA_real_, tolerance = NA_real_, compatible = NA)
        stopifnot(all(is.finite(tab$chisq)), all(is.finite(tab$p)), all(tab$df == 1))
        if (model %in% names(published)) {
            reference <- published[[model]]
            stopifnot(setequal(tab$term, names(reference)))
            tab$source_chisq <- unname(reference[tab$term])
            tab$delta_chisq <- tab$chisq - tab$source_chisq
            # Absolute + relative numerical tolerance accommodates package versions.
            tab$tolerance <- .005 + .005 * abs(tab$source_chisq)
            tab$compatible <- abs(tab$delta_chisq) <= tab$tolerance
        }
        ct <- fit_contrasts(model, fit)
        coefficients[[model]] <- co
        tests[[model]] <- tab
        contrasts[[model]] <- ct
        diag_row$usable <- TRUE
    }, warning = function(w) {
        warnings_seen <<- c(warnings_seen, conditionMessage(w))
        invokeRestart("muffleWarning")
    }), error = function(e) {
        diag_row$error <<- conditionMessage(e)
    })
    diag_row$warnings <- paste(unique(warnings_seen), collapse = "; ")
    diagnostics[[model]] <- diag_row
}
write_table <- function(rows, name) {
    if (length(rows)) write.csv(do.call(rbind, rows), file.path(out_dir, name), row.names = FALSE, na = "")
}
write_table(diagnostics, "model_diagnostics.csv")
write_table(tests, "model_tests.csv")
write_table(coefficients, "model_coefficients.csv")
write_table(contrasts, "conditional_contrasts.csv")
print(do.call(rbind, diagnostics)[c("model", "n", "convergence", "positive_definite_hessian", "usable", "error")])
if (!all(vapply(diagnostics, function(row) row$usable, logical(1))))
    stop("At least one model was unusable; inspect model_diagnostics.csv")
reference_rows <- subset(do.call(rbind, tests), !is.na(source_chisq))
message(nrow(reference_rows), " published tests compared; maximum absolute chi-square deviation: ",
        format(max(abs(reference_rows$delta_chisq)), digits = 6))
if (!all(reference_rows$compatible)) {
    print(subset(reference_rows, !compatible))
    stop("Replayed Type II tests differ from the archived results beyond the stated tolerance")
}
