# ---------- Build Stage ----------
    FROM eclipse-temurin:17-jdk AS build
    WORKDIR /workspace
    
    # Install Maven (or use a maven base image instead)
    RUN apt-get update && apt-get install -y maven
    
    # Copy pom.xml + src first (to leverage Docker caching)
    COPY pom.xml .
    COPY src ./src
    
    # Build JAR (skip tests for faster builds)
    RUN mvn clean package -DskipTests
    
    # ---------- Runtime Stage ----------
    FROM eclipse-temurin:17-jre
    WORKDIR /app
    
    # Copy only the built jar from build stage
    COPY --from=build /workspace/target/*.jar app.jar
    
    EXPOSE 8080
    ENTRYPOINT ["java","-jar","app.jar"]
    