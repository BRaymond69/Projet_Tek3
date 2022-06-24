##
## Makefile
##

NAME	=	pbrain-gomoku-ai

SELECTED_BRAIN	=	pbrain-eval.py

all:	$(NAME)

$(NAME):
	cp ${SELECTED_BRAIN} ${NAME}
	chmod +x ${NAME}

windows:
	./windows_build.py

clean:
	rm -f ${NAME}
	rm -rf build

fclean:	clean
	rm -rf dist

re:	fclean	all
