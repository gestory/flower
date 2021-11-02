class Statistics(object):
    """
    {
    1: {            # Level 1
        1: 0.7, 0,  # Size 1, mean is 0.7, zero errors
        2: 1.5, 1,
        3: None, 25
    },
    2: {
    ...
    }}
    """
    def __init__(self, user_id):
        self.user_id = user_id
        self.statistics = {}
        
    def update(self, level: int, size: int, data: list, errors: int):
        if data:
            mean_time = round(sum(data) / len(data), 2)
        else:
            mean_time = None

        try:
            self.statistics[level].update({size: (mean_time, errors)})
        except KeyError:
            self.statistics[level] = {size: (mean_time, errors)}
    
    def mean(self, level):
        try:
            data = [e[0] for e in self.statistics[level].values() if e[0]]
            if data:
                return str(round(sum(data) / len(data), 2))
            else:
                return 'N/A'
        except KeyError:
            return 'N/A'
        
    def get_data(self, level, size):
        level_data = self.statistics.get(level, None)
        if not level_data:
            return 'N/A'
        size_data = level_data.get(size, None)
        if not size_data:
            return 'N/A'
        if not size_data[0]:
            if not size_data[1]:
                return 'N/A'
            else:
                return 'Errors: {}'.format(size_data[1])
        if not size_data[1]:
            return str(size_data[0])
        else:
            return str(size_data[0]) + ' (Errors: {})'.format(size_data[1])
    
    def get_results(self):
        results_table = (("Size", "1 symbol", "4 symbols", "7 symbols", "10 symbols"),
                         ("1", self.get_data(1, 1), self.get_data(2, 1), self.get_data(3, 1), self.get_data(4, 1)),
                         ("2", self.get_data(1, 2), self.get_data(2, 2), self.get_data(3, 2), self.get_data(4, 2)),
                         ("3", self.get_data(1, 3), self.get_data(2, 3), self.get_data(3, 3), self.get_data(4, 3)),
                         ("4", self.get_data(1, 4), self.get_data(2, 4), self.get_data(3, 4), self.get_data(4, 4)),
                         ("5", self.get_data(1, 5), self.get_data(2, 5), self.get_data(3, 5), self.get_data(4, 5)),
                         ("Mean:", self.mean(1), self.mean(2), self.mean(3), self.mean(4)))
        return results_table

    def clear_results(self):
        self.statistics = {}
