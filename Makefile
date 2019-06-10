build:
	docker build -t soccerbot .

run:
	docker run --rm -v `pwd`:/app soccerbot

run-shell:
	docker run --rm -it -v `pwd`:/app soccerbot sh
