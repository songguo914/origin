CFLAGS	=	-UDEBUG -g -I$(HOME)/inc -I$(HOME)/inc/table -I$(INFORMIXDIR)/incl/esql -I$(HOME)/eusp/inc -I$(HOME)/inc/security
LIBRARY =	$(HOME)/lib
LIBKER	=	$(HOME)/eusp/lib
RUNDIR	=	$(HOME)/bt
ESQL	=	$(INFORMIXDIR)/bin/esql  
CP		=	cp
CC		=	esql
EXEC	=	btmainwatch
LIBS= $(HOME)/lib $(HOME)/eusp/lib
#LIBKERN = $(HOME)/lib/libke.a
.SUFFIXES: 
.SUFFIXES: .o .ec

OBJS	= \
	btcombintbl.o \
	cbtfunc.o\
	t9800.o
	

btmainwatch: $(OBJS) 
	buildclient -f  "$(OBJS) -lm -lld  -L$(LIBRARY) -lKvhsmapi  -lbc  -lfc -lcf -ldb  -leti -lcurses -L$(LIBKER) -leusp" -o $(EXEC) -w  
	@touch btcombintbl.ec
	$(CP)  $(EXEC) $(RUNDIR)
.ec.o :	
	$(ESQL)	$(CFLAGS)  -c $*.ec
	rm $*.c
