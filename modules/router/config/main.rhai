fn supergraph_service(service) {
  let add_cookies_to_response = |response| {
    if response.context["set_cookie_headers"]?.len > 0 {
      response.headers["set-cookie"] = response.context["set_cookie_headers"];
    }
    if response.context["front_token"]?.len > 0 {
      response.headers["front-token"] = response.context["front_token"];
    }
    if response.context["st_access_token"]?.len > 0 {
      response.headers["st-access-token"] = response.context["st_access_token"];
    }
    if response.context["st_refresh_token"]?.len > 0 {
      response.headers["st-refresh-token"] = response.context["st_refresh_token"];
    }
    if response.context["access_control_expose_headers"]?.len > 0 {
      response.headers["access-control-expose-headers"] = response.context["access_control_expose_headers"];
    }
  };

  service.map_response(add_cookies_to_response);
}

fn subgraph_service(service, subgraph) {
  let store_cookies_from_subgraphs = |response| {
    if "set-cookie" in response.headers {
      if response.context["set_cookie_headers"] == () {
        response.context.set_cookie_headers = []
      }
      response.context.set_cookie_headers += response.headers.values("set-cookie");
    }
    if "front-token" in response.headers {
      if response.context["front_token"] == () {
        response.context.front_token = []
      }
      response.context.front_token += response.headers.values("front-token");
    }
    if "st-access-token" in response.headers {
      if response.context["st_access_token"] == () {
        response.context.st_access_token = []
      }
      response.context.st_access_token += response.headers.values("st-access-token");
    }
    if "st-refresh-token" in response.headers {
      if response.context["st_refresh_token"] == () {
        response.context.st_refresh_token = []
      }
      response.context.st_refresh_token += response.headers.values("st-refresh-token");
    }
    if "access-control-expose-headers" in response.headers {
      if response.context["access_control_expose_headers"] == () {
        response.context.access_control_expose_headers = []
      }
      response.context.access_control_expose_headers += response.headers.values("access-control-expose-headers");
    }
  };

  service.map_response(store_cookies_from_subgraphs);
}