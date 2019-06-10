build:
	docker build -t soccerbot .

run:
	docker run --rm -v `pwd`:/app --env-file=.env soccerbot

run-shell:
	docker run --rm -it -v `pwd`:/app --env-file=.env soccerbot sh
