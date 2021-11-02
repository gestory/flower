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
    
    def __mean(self, level):
        try:
            data = [e[0] for e in self.statistics[level].values() if e[0]]
            if data:
                return round(sum(data) / len(data), 2)
        except KeyError:
            return None
    
    def mean(self, level) -> str:
        try:
            mean = self.__mean(level)
            if mean:
                return str(mean)
            else:
                return 'N/A'
        except KeyError:
            return 'N/A'
        
    def get_data(self, level, size) -> str:
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
        return results_table, [self.k1, self.k2, self.k3]

    def clear_results(self):
        self.statistics = {}
    
    @property
    def k1(self):
        mean_1 = self.__mean(1)
        mean_2 = self.__mean(2)
        if mean_1 and mean_2:
            return str(round(mean_2 / mean_1, 2))
        else:
            return 'N/A'

    @property
    def k2(self):
        mean_1 = self.__mean(1)
        mean_3 = self.__mean(3)
        if mean_1 and mean_3:
            return str(round(mean_3 / mean_1, 2))
        else:
            return 'N/A'

    @property
    def k3(self):
        mean_1 = self.__mean(1)
        mean_4 = self.__mean(4)
        if mean_1 and mean_4:
            return str(round(mean_4 / mean_1, 2))
        else:
            return 'N/A'
