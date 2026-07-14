FROM eclipse-temurin:21-jre
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=75"
COPY app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
