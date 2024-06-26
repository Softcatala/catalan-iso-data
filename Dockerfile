FROM python:3.11-slim as builder

RUN pip install pipenv

WORKDIR "/app"

COPY . /app/

RUN pipenv requirements > requirements.txt

RUN pip install -r requirements.txt

RUN mkdir -p output
RUN python generate.py

RUN ls output

FROM softcatala/sc-static-file-server:1.3

COPY --from=builder /app/output/* /static/

ENTRYPOINT [ "/scStaticFileServer" ]
