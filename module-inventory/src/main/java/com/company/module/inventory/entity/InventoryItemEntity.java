package com.company.module.inventory.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Inventory Item Entity.
 * Table prefix: MOD_INVENTORY_
 * Mapped to OracleDB via inventoryEntityManagerFactory.
 */
@Entity
@Table(name = "MOD_INVENTORY_ITEMS")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryItemEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "inventory_item_seq")
    @SequenceGenerator(
            name = "inventory_item_seq",
            sequenceName = "MOD_INVENTORY_ITEMS_SEQ",
            allocationSize = 1
    )
    @Column(name = "ITEM_ID")
    private Long itemId;

    @Column(name = "ITEM_CODE", nullable = false, unique = true, length = 50)
    private String itemCode;

    @Column(name = "ITEM_NAME", nullable = false, length = 200)
    private String itemName;

    @Column(name = "CATEGORY", length = 100)
    private String category;

    @Column(name = "QUANTITY", nullable = false)
    private Integer quantity;

    @Column(name = "UNIT_PRICE", precision = 18, scale = 2)
    private BigDecimal unitPrice;

    @Column(name = "STORAGE_LOCATION", length = 200)
    private String storageLocation;

    @Column(name = "DESCRIPTION", length = 500)
    private String description;

    @Column(name = "USE_YN", nullable = false, length = 1)
    @Builder.Default
    private String useYn = "Y";

    @Column(name = "CREATED_AT", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "UPDATED_AT")
    private LocalDateTime updatedAt;

    @Column(name = "CREATED_BY", length = 50)
    private String createdBy;

    @Column(name = "UPDATED_BY", length = 50)
    private String updatedBy;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
