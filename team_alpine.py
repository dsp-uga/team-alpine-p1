import argparse
from src.models.logistic_regression import log_reg


parser = argparse.ArgumentParser(description='Model Parameters:')
parser.add_argument('--model', dest='model', default='rf', choices=['nb', 'lr', 'rf'],
                    help='machine learning model to be used')
parser.add_argument('--n_gram', dest='n_gram_value', type='int', default=1, choices=[1, 2, 3],
                    help='value of n-gram to be applied to features')
parser.add_argument('--pca', dest='pca_value', type='boolean', default=False, choices=[True, False],
                    help='enable/disable dimensionality reduction using Principal Component Analysis')
parser.add_argument('--cv', dest='cv_value', type='boolean', default=False, choices=[True, False],
                    help='enable/disable 5-fold cross-validation')
parser.add_argument('--oversampling', dest='oversampling_val', default=False, choices=[True, False], type='boolean',
                    help='enable/disable oversampling')
parser.add_argument('--use-asm', dest='asm', default=True, type='boolean', choices=[True, False],
                    help='use assembly files with byte files as features')

args = parser.parse_args()
n_gram_val = args.n_gram_value
pca_val = args.pca_value
cv_val = args.cv_value
oversampling_val = args.oversampling_val
use_asm_val = args.use_asm

if args.model == 'nb':
    pass
elif args.model == 'lr':
    log_reg(n_gram_val, pca_val, cv_val, oversampling_val, use_asm_val)
elif args.model == 'rf':
    pass
