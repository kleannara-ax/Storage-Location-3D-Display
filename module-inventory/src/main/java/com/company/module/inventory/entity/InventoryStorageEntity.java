package com.company.module.inventory.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

/**
 * Inventory Storage Location Entity.
 * Table prefix: MOD_INVENTORY_
 * Represents 3D storage location coordinates.
 */
@Entity
@Table(name = "MOD_INVENTORY_STORAGE_LOCATIONS")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryStorageEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "inventory_storage_seq")
    @SequenceGenerator(
            name = "inventory_storage_seq",
            sequenceName = "MOD_INVENTORY_STORAGE_SEQ",
            allocationSize = 1
    )
    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "LOCATION_CODE", nullable = false, unique = true, length = 50)
    private String locationCode;

    @Column(name = "LOCATION_NAME", nullable = false, length = 200)
    private String locationName;

    @Column(name = "ZONE", length = 50)
    private String zone;

    @Column(name = "COORD_X")
    private Double coordX;

    @Column(name = "COORD_Y")
    private Double coordY;

    @Column(name = "COORD_Z")
    private Double coordZ;

    @Column(name = "CAPACITY")
    private Integer capacity;

    @Column(name = "CURRENT_USAGE")
    @Builder.Default
    private Integer currentUsage = 0;

    @Column(name = "USE_YN", nullable = false, length = 1)
    @Builder.Default
    private String useYn = "Y";

    @Column(name = "CREATED_AT", updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "UPDATED_AT")
    private LocalDateTime updatedAt;

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
