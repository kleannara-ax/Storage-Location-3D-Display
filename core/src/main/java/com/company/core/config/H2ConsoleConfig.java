package com.company.core.config;

import org.h2.tools.Server;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.web.servlet.ServletRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Custom H2 Console configuration that forces webAllowOthers=true.
 * Spring Boot's built-in h2.console.settings.web-allow-others property
 * may not take effect behind a reverse proxy; this explicitly registers
 * the H2 Console servlet with remote access enabled.
 */
@Configuration
@ConditionalOnProperty(name = "spring.h2.console.enabled", havingValue = "true")
public class H2ConsoleConfig {

    @Bean
    public ServletRegistrationBean<org.h2.server.web.JakartaWebServlet> h2ConsoleServlet() {
        ServletRegistrationBean<org.h2.server.web.JakartaWebServlet> registration =
                new ServletRegistrationBean<>(new org.h2.server.web.JakartaWebServlet());
        registration.addUrlMappings("/h2-console/*");
        registration.addInitParameter("webAllowOthers", "true");
        registration.setLoadOnStartup(1);
        return registration;
    }
}
