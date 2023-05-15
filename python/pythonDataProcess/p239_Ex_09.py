import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic' #Matplotlib의 기본 글꼴을 'Malgun Gothic'으로 설정

myindex = ['이상화', '한용운','노천명','윤동주', '이육사']
mylist = [30, 20, 40, 60, 50]
mycolors = ['blue', '#6AFF00', 'yellow', '#FF003C', 'green']

plt.pie(x=mylist, labels=myindex, shadow=True, explode=(0, 0.1, 0, 0, 0),
        colors=mycolors, autopct='%1.2f%%', startangle=90, counterclock=False)

plt.legend(loc=4)

filename = 'pieGraph02.png'
plt.savefig(filename, dpi=400, bbox_inches='tight')
print(filename + ' Saved...')
plt.show()