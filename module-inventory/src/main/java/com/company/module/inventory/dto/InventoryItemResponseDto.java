package com.company.module.inventory.dto;

import com.company.module.inventory.entity.InventoryItemEntity;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryItemResponseDto {

    private Long itemId;
    private String itemCode;
    private String itemName;
    private String category;
    private Integer quantity;
    private BigDecimal unitPrice;
    private String storageLocation;
    private String description;
    private String useYn;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    /**
     * Entity -> DTO conversion
     */
    public static InventoryItemResponseDto fromEntity(InventoryItemEntity entity) {
        return InventoryItemResponseDto.builder()
                .itemId(entity.getItemId())
                .itemCode(entity.getItemCode())
                .itemName(entity.getItemName())
                .category(entity.getCategory())
                .quantity(entity.getQuantity())
                .unitPrice(entity.getUnitPrice())
                .storageLocation(entity.getStorageLocation())
                .description(entity.getDescription())
                .useYn(entity.getUseYn())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
    }
}
