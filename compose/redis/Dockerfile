FROM redis:4-alpine

RUN apk add --no-cache \
        tzdata

# Set Timezone
RUN cp /usr/share/zoneinfo/Asia/Bangkok /etc/localtime
RUN echo "Asia/Bangkok" > /etc/timezone

CMD ["redis-server", "--appendonly", "yes"]
