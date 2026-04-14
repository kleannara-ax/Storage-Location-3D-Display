package com.company.module.inventory.config;

import jakarta.persistence.EntityManagerFactory;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.autoconfigure.jdbc.DataSourceProperties;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.orm.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import org.springframework.beans.factory.annotation.Value;

import javax.sql.DataSource;
import java.util.HashMap;
import java.util.Map;

/**
 * OracleDB DataSource configuration for module-inventory.
 * This module uses a separate Oracle database, isolated from the default MariaDB.
 * Core module is NOT modified - this config is self-contained within the inventory module.
 *
 * Dialect and ddl-auto are configurable via properties for local/test profiles.
 */
@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(
        basePackages = "com.company.module.inventory.repository",
        entityManagerFactoryRef = "inventoryEntityManagerFactory",
        transactionManagerRef = "inventoryTransactionManager"
)
public class InventoryDataSourceConfig {

    @Value("${inventory.jpa.hibernate.dialect:org.hibernate.dialect.OracleDialect}")
    private String hibernateDialect;

    @Value("${inventory.jpa.hibernate.ddl-auto:none}")
    private String ddlAuto;

    // ============================================================
    // DataSource Properties (from application.yml -> spring.datasource.inventory)
    // ============================================================
    @Bean(name = "inventoryDataSourceProperties")
    @ConfigurationProperties(prefix = "spring.datasource.inventory")
    public DataSourceProperties inventoryDataSourceProperties() {
        return new DataSourceProperties();
    }

    @Bean(name = "inventoryDataSource")
    public DataSource inventoryDataSource() {
        return inventoryDataSourceProperties()
                .initializeDataSourceBuilder()
                .build();
    }

    // ============================================================
    // EntityManagerFactory (dialect configurable for local H2 / prod Oracle)
    // ============================================================
    @Bean(name = "inventoryEntityManagerFactory")
    public LocalContainerEntityManagerFactoryBean inventoryEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("inventoryDataSource") DataSource dataSource) {

        Map<String, Object> properties = new HashMap<>();
        properties.put("hibernate.hbm2ddl.auto", ddlAuto);
        properties.put("hibernate.dialect", hibernateDialect);
        properties.put("hibernate.show_sql", true);
        properties.put("hibernate.format_sql", true);

        return builder
                .dataSource(dataSource)
                .packages("com.company.module.inventory.entity")
                .persistenceUnit("inventoryPU")
                .properties(properties)
                .build();
    }

    // ============================================================
    // TransactionManager for OracleDB
    // ============================================================
    @Bean(name = "inventoryTransactionManager")
    public PlatformTransactionManager inventoryTransactionManager(
            @Qualifier("inventoryEntityManagerFactory") EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }
}
