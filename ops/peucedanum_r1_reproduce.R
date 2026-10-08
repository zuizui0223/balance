suppressPackageStartupMessages({
  library(lme4)
  library(emmeans)
  library(dplyr)
})

plot_order <- c("HA", "HL", "HC", "KD", "HD")
published_S <- c(HA=-0.027, HL=-0.051, HC=0.036, KD=0.021, HD=0.024)
published_beta <- c(HA=-0.035, HL=-0.029, HC=0.034, KD=0.008, HD=0.026)
published_b <- c(HA=0.63, HL=0.45, HC=1.15, KD=1.26, HD=1.55)

data1 <- read.csv("All_Plots_Data.csv", header=TRUE)
data1$Plot <- factor(data1$Plot, levels=plot_order)
data1$Fertilization_rate <- data1$InitialFruitN/data1$HflowerN
data1$Fruitset_rate <- data1$FinalFruitN/data1$HflowerN
data1$Floral_gender <- data1$MflowerN/(data1$HflowerN+data1$MflowerN)

scale_plot <- function(d) {
  d$HflowerN_s <- as.numeric(scale(d$HflowerN))
  d$MflowerN_s <- as.numeric(scale(d$MflowerN))
  d$Height_s <- as.numeric(scale(d$Height))
  d
}

parts <- lapply(plot_order, function(p) scale_plot(subset(data1, Plot==p)))
names(parts) <- plot_order
means <- c(HA=3.151, HL=11.78, HC=10.22, KD=18.49, HD=15.07)
for (p in plot_order) {
  parts[[p]]$Fitness <- parts[[p]]$FinalFruitN/means[[p]]
}
dataRB <- do.call(rbind, parts)
dataRB$HflowerN_s_2 <- dataRB$HflowerN_s^2
dataRB$MflowerN_s_2 <- dataRB$MflowerN_s^2
dataRB$Height_s_2 <- dataRB$Height_s^2
dataRB <- subset(dataRB, !is.na(InitialFruitN))
# Original archived R_script_Kudo&Shibata.R also removes Height NA globally
# *before* computing differentials, multivariable gradients, and nls female gain.
dataRB <- subset(dataRB, !is.na(Height))
cat('source-global complete-case rows:',nrow(dataRB),'\n')

extract_adjusted <- function(trend_model, response_model, data, var) {
  # The archived source computes trends from the named-square twin model,
  # but response-scale adjustments from the I(x^2) model.
  tr <- as.data.frame(emtrends(trend_model, ~ Plot, var=var, data=data))
  # lme4 drops incomplete model-specific rows (notably HD Height NA).
  # Predict only for rows actually included in the fitted model.
  mf <- model.frame(response_model)
  pred <- as.numeric(predict(response_model, type="response"))
  if (length(pred) != nrow(mf) || any(!is.finite(pred))) {
    stop("fitted values and model-frame rows do not match")
  }
  constants <- data.frame(Plot=mf$Plot, v=pred*(1-pred)) |>
    group_by(Plot) |>
    summarise(constant=mean(v), fitted_n=dplyr::n(), .groups="drop")
  if (any(!is.finite(constants$constant)) || any(constants$fitted_n < 1L)) {
    stop("non-finite or unsupported fitted-row logistic adjustment")
  }
  merged <- merge(tr, constants, by="Plot", sort=FALSE)
  trend_name <- grep("\\.trend$", names(merged), value=TRUE)
  if (length(trend_name) != 1) stop("could not identify emtrends estimate column")
  merged$adjusted_estimate <- merged[[trend_name]] * merged$constant
  merged$adjusted_se <- merged$SE * merged$constant
  merged[match(plot_order, merged$Plot), ]
}

data_grad <- subset(dataRB, !is.na(FinalFruitN))
glmerMR <- glmer(
  Fruitset_rate ~
    HflowerN_s*Plot + MflowerN_s*Plot + Height_s*Plot +
    I(HflowerN_s^2)*Plot + I(MflowerN_s^2)*Plot + I(Height_s^2)*Plot +
    (1|Year),
  data=data_grad,
  weights=HflowerN,
  family=binomial,
  control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=2e5))
)
glmerMR_t <- glmer(
  Fruitset_rate ~
    HflowerN_s*Plot + MflowerN_s*Plot + Height_s*Plot +
    HflowerN_s_2*Plot + MflowerN_s_2*Plot + Height_s_2*Plot +
    (1|Year),
  data=data_grad,
  weights=HflowerN,
  family=binomial,
  control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=2e5))
)
grad <- extract_adjusted(glmerMR_t, glmerMR, data_grad, "HflowerN_s")

data_diff <- subset(dataRB, !is.na(FinalFruitN))
glmerDMR <- glmer(
  Fruitset_rate ~ HflowerN_s*Plot + I(HflowerN_s^2)*Plot + (1|Year),
  data=data_diff,
  weights=HflowerN,
  family=binomial,
  control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=2e5))
)
glmerDMR_t <- glmer(
  Fruitset_rate ~ HflowerN_s*Plot + HflowerN_s_2*Plot + (1|Year),
  data=data_diff,
  weights=HflowerN,
  family=binomial,
  control=glmerControl(optimizer="bobyqa", optCtrl=list(maxfun=2e5))
)
diff <- extract_adjusted(glmerDMR_t, glmerDMR, data_diff, "HflowerN_s")

gain_rows <- list()
for (p in plot_order) {
  d <- subset(dataRB, Plot==p)
  start_a <- if (p=="HD") 0.01 else 0.1
  fit <- nls(Fitness ~ a*HflowerN^b, start=list(a=start_a,b=1), data=d)
  s <- summary(fit)$parameters
  gain_rows[[p]] <- data.frame(
    Plot=p,
    a=unname(coef(fit)[["a"]]),
    a_se=s["a","Std. Error"],
    b=unname(coef(fit)[["b"]]),
    b_se=s["b","Std. Error"],
    fitted_n=length(fitted(fit))
  )
}
gain <- do.call(rbind, gain_rows)

out <- data.frame(
  Plot=plot_order,
  S=diff$adjusted_estimate,
  S_se=diff$adjusted_se,
  S_fitted_n=diff$fitted_n,
  beta=grad$adjusted_estimate,
  beta_se=grad$adjusted_se,
  beta_fitted_n=grad$fitted_n,
  female_gain_b=gain$b,
  female_gain_b_se=gain$b_se,
  female_gain_fitted_n=gain$fitted_n,
  published_S=unname(published_S[plot_order]),
  published_beta=unname(published_beta[plot_order]),
  published_b=unname(published_b[plot_order])
)
out$S_round3_match <- round(out$S,3) == out$published_S
out$beta_round3_match <- round(out$beta,3) == out$published_beta
out$b_round2_match <- round(out$female_gain_b,2) == out$published_b

write.csv(out, "PEUCEDANUM_2025_R1_REPRODUCTION.csv", row.names=FALSE)
writeLines(capture.output(sessionInfo()), "R_SESSION_INFO.txt")

cat("R1 source-model reproduction attempt (not automatically promoted)\n")
print(out, digits=10)
cat("all beta round3 match:", all(out$beta_round3_match), "\n")
cat("all S round3 match:", all(out$S_round3_match), "\n")
cat("all b round2 match:", all(out$b_round2_match), "\n")
