from collections import Counter


y_train_file = open("../../data/y_train.txt", "r")
lines = list(y_train_file)
label_counter = dict(Counter(lines))
print(label_counter)
