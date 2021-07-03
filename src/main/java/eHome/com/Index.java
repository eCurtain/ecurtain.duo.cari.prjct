package eHome.com;

import org.springframework.web.bind.annotation.GetMapping;

import reactor.core.publisher.Mono;

public class Index {

  @GetMapping("/index")
  public Mono<String> getIndex() {
    return Mono.just("Hello World!");
  }
}
