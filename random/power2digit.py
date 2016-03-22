def sum_digits3(n):
   r = 0
   while n:
       r, n = r + n % 10, n / 10
   return r

for j in range(2,10):
	for i in range(2,1000):
		if i == sum_digits3(pow(j,i)):
			print j,i,pow(j,i)
			break

