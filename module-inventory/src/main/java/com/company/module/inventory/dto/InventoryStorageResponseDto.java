package com.company.module.inventory.dto;

import com.company.module.inventory.entity.InventoryStorageEntity;
import lombok.*;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryStorageResponseDto {

    private Long locationId;
    private String locationCode;
    private String locationName;
    private String zone;
    private Double coordX;
    private Double coordY;
    private Double coordZ;
    private Integer capacity;
    private Integer currentUsage;
    private String useYn;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    /**
     * Entity -> DTO conversion
     */
    public static InventoryStorageResponseDto fromEntity(InventoryStorageEntity entity) {
        return InventoryStorageResponseDto.builder()
                .locationId(entity.getLocationId())
                .locationCode(entity.getLocationCode())
                .locationName(entity.getLocationName())
                .zone(entity.getZone())
                .coordX(entity.getCoordX())
                .coordY(entity.getCoordY())
                .coordZ(entity.getCoordZ())
                .capacity(entity.getCapacity())
                .currentUsage(entity.getCurrentUsage())
                .useYn(entity.getUseYn())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
    }
}
