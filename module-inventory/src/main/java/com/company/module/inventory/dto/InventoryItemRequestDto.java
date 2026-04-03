package com.company.module.inventory.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;

import java.math.BigDecimal;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryItemRequestDto {

    @NotBlank(message = "Item code is required")
    @Size(max = 50, message = "Item code must be 50 characters or less")
    private String itemCode;

    @NotBlank(message = "Item name is required")
    @Size(max = 200, message = "Item name must be 200 characters or less")
    private String itemName;

    @Size(max = 100, message = "Category must be 100 characters or less")
    private String category;

    @NotNull(message = "Quantity is required")
    @Min(value = 0, message = "Quantity must be 0 or more")
    private Integer quantity;

    private BigDecimal unitPrice;

    @Size(max = 200, message = "Storage location must be 200 characters or less")
    private String storageLocation;

    @Size(max = 500, message = "Description must be 500 characters or less")
    private String description;
}
