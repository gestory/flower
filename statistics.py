class Statistics(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.statistics = {}
        
    def update(self, key, value):
        try:
            self.statistics[key].append(value)
        except KeyError:
            self.statistics[key] = [value]
    
    def mean(self, level, size=0):
        if not size:
            try:
                return str(round(sum(self.statistics[level])/len(self.statistics[level]), 2))
            except KeyError:
                return "N/A"
        acc = 0
        start_index = (size-1) * 5
        
        for i in range(5):
            try:
                value = self.statistics[level][start_index+i]
            except KeyError:
                value = 0
            acc += value
        return str(round(acc / 5, 2))
    
    def get_results(self):
        results_table = (("Size", "1 symbol", "4 symbols", "7 symbols", "10 symbols"),
                         ("1", self.mean(1, 1), self.mean(2, 1), self.mean(3, 1), self.mean(4, 1)),
                         ("2", self.mean(1, 2), self.mean(2, 2), self.mean(3, 2), self.mean(4, 2)),
                         ("3", self.mean(1, 3), self.mean(2, 3), self.mean(3, 3), self.mean(4, 3)),
                         ("4", self.mean(1, 4), self.mean(2, 4), self.mean(3, 4), self.mean(4, 4)),
                         ("5", self.mean(1, 5), self.mean(2, 5), self.mean(3, 5), self.mean(4, 5)),
                         ("Mean:", self.mean(1), self.mean(2), self.mean(3), self.mean(4)))
        return results_table

    def clear_results(self):
        self.statistics = {}
