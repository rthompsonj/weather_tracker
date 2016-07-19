build:
	docker build -t weather .
run:
	docker run -itd -p 5000:5000 --name=WEATHER weather
clean:
	docker rm WEATHER
