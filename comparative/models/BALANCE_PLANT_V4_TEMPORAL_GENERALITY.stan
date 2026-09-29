// BALANCE plant model v4 temporal-generality sensitivity.
// Adds only the preregistered U6 x ORDERED_OR_ALTERNATING interaction.
data {
  int<lower=1> N;
  int<lower=2> K;
  int<lower=2> U;
  int<lower=1> P;
  matrix[N, P] X;
  array[N] int<lower=1, upper=K> y;
  array[N] int<lower=1, upper=U> universe;
  array[N] int<lower=0, upper=1> u6_ordered;
  real<lower=0> slope_prior_sd;
  real<lower=0> intercept_prior_sd;
  real<lower=0> interaction_prior_sd;
}
parameters {
  matrix[U, K - 1] alpha;
  matrix[P, K - 1] beta;
  vector[K - 1] gamma_u6_ordered;
}
model {
  to_vector(alpha) ~ normal(0, intercept_prior_sd);
  to_vector(beta) ~ normal(0, slope_prior_sd);
  gamma_u6_ordered ~ normal(0, interaction_prior_sd);

  for (n in 1:N) {
    vector[K] eta;
    eta[1] = 0;
    for (k in 2:K) {
      eta[k] =
        alpha[universe[n], k - 1]
        + X[n] * beta[, k - 1]
        + u6_ordered[n] * gamma_u6_ordered[k - 1];
    }
    y[n] ~ categorical_logit(eta);
  }
}
generated quantities {
  array[N] real log_lik;
  matrix[N, K] category_probability;

  for (n in 1:N) {
    vector[K] eta;
    vector[K] prob;
    eta[1] = 0;
    for (k in 2:K) {
      eta[k] =
        alpha[universe[n], k - 1]
        + X[n] * beta[, k - 1]
        + u6_ordered[n] * gamma_u6_ordered[k - 1];
    }
    prob = softmax(eta);
    log_lik[n] = categorical_logit_lpmf(y[n] | eta);
    for (k in 1:K) {
      category_probability[n, k] = prob[k];
    }
  }
}
