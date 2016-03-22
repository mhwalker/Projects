CPP=g++
CC=gcc
OBJS=Person.o
INCLUDES=-I/sw/include/root
CPPFLAGS=-L/sw/lib/root -ldl -lNew \
	-lCore  -lCint -lRIO -lNet -lHist -lThread \
        -lGraf -lGraf3d -lGpad -lTree -lMatrix -lMathCore -lRint \

popsim: popsim.o $(OBJS)
	$(CPP) -o popsim popsim.o $(OBJS) $(CPPFLAGS)

popsim.o: popsim.cxx popsim.h Person.h
	$(CPP) -c popsim.cxx $(INCLUDES)

test: test.o $(OBJS)
	$(CPP) -o test test.o $(OBJS) $(CPPFLAGS)

test.o: test.cxx test.h Person.h
	$(CPP) -c test.cxx $(INCLUDES)

Person.o: Person.h Person.cxx
	$(CPP) -c Person.cxx

clean:
	-rm *~ *.o