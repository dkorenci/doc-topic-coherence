import numpy as np

def fiveNumberSummary(vals, string=False):
    '''
    :param vals: list-like of numbers
    :param string: return summary as string, in printable form
    :return:
    '''
    mn, mx = np.min(vals), np.max(vals)
    p = np.percentile(vals, [25, 50, 75])
    p25, med, p75 = p[0], p[1], p[2]
    result = (mn, p25, med, p75, mx)
    if string: return ' '.join('%.4f'%v for v in result)
    else: return result

class Stats():
    '''
    Calculates, stores and renders for printing statistical measures
     of a list of numbers.
    '''

    def __init__(self, vals):
        '''
        :param vals: list-like of numbers
        '''
        self.__calcStats(vals)
        self.vals = vals

    def __calcStats(self, vals):
        # five number summary
        self.N = len(vals)
        self.min, self.max = np.min(vals), np.max(vals)
        p = np.percentile(vals, [25, 50, 75])
        self.q25, self.median, self.q75 = p[0], p[1], p[2]
        # mean, variance, std. dev
        self.mean = np.mean(vals)
        self.std = np.std(vals)
        self.var = np.var(vals)

    def percLess(self, val):
        cnt = 0.0
        for v in self.vals:
            if v <= val: cnt += 1
        return cnt/self.N

    def __str__(self):
        return 'N %d, min %.4f , q25 %.4f, med %.4f, avg %.4f, q75 %.4f, max %.4f ; std %.4f' \
                % (self.N, self.min, self.q25, self.median,
                   self.mean, self.q75, self.max, self.std)