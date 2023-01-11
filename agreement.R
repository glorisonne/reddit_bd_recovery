# https://cran.r-project.org/web/packages/irrCAC/vignettes/overview.html
# benchmark the coefficient - what level of agreement does it map to?
# https://cran.r-project.org/web/packages/irrCAC/vignettes/benchmarking.html

library(irrCAC)

# crosstab is the crosstabulated agreement between the two coders in the format 
#           label_1 ...  label N
# label_1 x_1,1   ...  x_1,N     
# label_2 x_2,1   ...  x_1,2
# ...           x_i,j
# label_N x_N,1   ...  x_N,N
# where x_i,j is the number of instances in the dataset that coder 1 assigned
# label i and coder 2 assigned label j (see for an example below)
# this means that the number of agreements is the sum of the diagnoal

agreement <- function(crosstab) {
  print(crosstab)
  kappa <- kappa2.table(crosstab)
  print(paste("Cohen's Kappa k: ", round(kappa$coeff.val, 2), "SE: ", round(kappa$coeff.se, 2)))
  
  ac1 <- gwet.ac1.table(crosstab)
  print(paste("Gwet's AC1: ", round(ac1$coeff.val, 2), "SE: ", round(ac1$coeff.se, 2)))
  print("AC1 benchmarking:")
  print(altman.bf(ac1$coeff.val, ac1$coeff.se))
  
  print(paste("Observed agreement P0: ", round(sum(diag(as.table(data.matrix(crosstab))))/sum(as.table(data.matrix(crosstab))), 2)))
}

# Example: Table 20 Pilot
# 20 instances total, GJ (coder 1) and CH (coder 2) agree on PR relevant for
# 11 instances and not PR relevant for 4 instances.
# GJ coded PR relevant for two instances that CH coded as not relevant
# CH coded PR relevant for three instances that GJ coded as not relevant

df_pilot <- data.frame(c(11, 3), c(2,4))
agreement(df_pilot)