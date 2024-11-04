
FROM aptplatforms/oraclelinux-python

RUN pip install --upgrade pip && pip install oracledb

ENV DPI_DEBUG_LEVEL=64

WORKDIR /app

COPY /app /app/

CMD ["python", "/app/app.py"]
