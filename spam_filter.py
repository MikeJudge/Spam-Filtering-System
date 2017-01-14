############################################################
# CMPSC 442: Homework 7
############################################################

student_name = "Michael Judge"

############################################################
# Imports
############################################################

# Include your imports here, if any are used.
import email
import math
import os



def load_tokens(email_path):
    unigram_l = []
    bigram_l = []
    header_l = []
    t = ['']*2
    f = open(email_path, 'r')
    message = email.message_from_file(f)

    for line in email.iterators.body_line_iterator(message):
        for token in line.split():
            unigram_l.append(token)
            t = t[1:]
            t.append(token)
            bigram_l.append(' '.join(t))


    for line in message.values():
        for token in line.split():
            header_l.append(token)

    f.close()
    return [unigram_l, bigram_l, header_l]



def get_counts(email_paths):
    result = [[{}, 0], [{}, 0], [{}, 0]]

    for f in email_paths:
        l = load_tokens(f)
        for i in xrange(len(l)):

            curr_counts = result[i][0]

            for token in l[i]:
                result[i][1] += 1
                if token not in curr_counts:
                    curr_counts[token] = 1
                else:
                    curr_counts[token] += 1


    return result     


def log_probs(email_paths, smoothing):
    probs = []
    count_info = get_counts(email_paths)

    for counts, total_count in count_info:
        result = {}
        for token, count in counts.iteritems():
            result[token] = math.log(count + smoothing) - math.log(total_count + smoothing*(len(counts) + 1))
        result['<UNK>'] = math.log(smoothing) - math.log(total_count + smoothing*(len(counts) + 1))
        probs.append(result)

    return probs



############################################################
# Spam Filter
############################################################

class SpamFilter(object):

    # Note that the initialization signature here is slightly different than the
    # one in the previous homework. In particular, any smoothing parameters used
    # by your model will have to be hard-coded in.

    def __init__(self, spam_dir, ham_dir):
    	smoothing = 1e-15
        self.spam_l = log_probs([(spam_dir + '/' + f) for f in os.listdir(spam_dir)], smoothing)
        self.ham_l = log_probs([(ham_dir + '/' + f) for f in os.listdir(ham_dir)], smoothing)

        num_spam = len(os.listdir(spam_dir))
        num_ham = len(os.listdir(ham_dir))

        self.prob_spam = math.log(num_spam) - math.log(num_spam + num_ham)
        self.prob_ham = math.log(num_ham) - math.log(num_spam + num_ham)




    def is_spam(self, email_path):
    	spam_num = float(0)
        ham_num = float(0)
        count_info = get_counts([email_path])

        for i in xrange(len(count_info)):
            counts = count_info[i][0]
            spam_dict = self.spam_l[i]
            ham_dict = self.ham_l[i]

            for token, count in counts.iteritems():
                if token in spam_dict:
                    spam_num += count * spam_dict[token]
                else:
                    spam_num += count * spam_dict['<UNK>']

                if token in ham_dict:
                    ham_num += count * ham_dict[token]
                else:
                    ham_num += count * ham_dict['<UNK>']

            ham_num += (3.0 * self.prob_ham)
            spam_num += (3.0 * self.prob_spam)

        return spam_num > ham_num

sf = SpamFilter('data/train/spam', 'data/train/ham')
spam_correct = 0;
ham_correct = 0;
for f in os.listdir('data/dev/spam'):
    if sf.is_spam('data/dev/spam/' + f):
        spam_correct += 1

for f in os.listdir('data/dev/ham'):
    if not sf.is_spam('data/dev/ham/' + f):
        ham_correct += 1

print 'spam_success = ' + str(1.0*spam_correct/len(os.listdir('data/dev/spam')))
print 'ham_success = ' + str(1.0*ham_correct/len(os.listdir('data/dev/ham')))

