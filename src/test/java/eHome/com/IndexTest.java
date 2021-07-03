package eHome.com;

import org.junit.jupiter.api.Test;
import org.springframework.web.reactive.function.client.WebClient;

import static org.junit.jupiter.api.Assertions.*;

class IndexTest {
  @Test
  void testIndex(){
    WebClient.create("http://localhost:8080/index").get()
        .retrieve()
        .bodyToMono(String.class)
        .doOnNext(s -> System.out.println(s));
  }
}