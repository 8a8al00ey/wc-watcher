RUN := docker run --rm -it -v `pwd`:/app --env-file=.env soccerbot

build:
	docker build -t soccerbot .

run:
	$(RUN)

run-shell:
	$(RUN) sh

run-daemon: build
	docker run --rm -it -d --env-file=.env soccerbot
