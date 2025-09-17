class UserProgress:
    def __init__(self, name, progress, level, score, nextLevelStart,isMaxLevel):
        self.subjectName = name
        self.progressPercentage = progress
        self.level = level
        self.score = score
        self.nextLevelStart = nextLevelStart
        self.isMaxLevel = isMaxLevel