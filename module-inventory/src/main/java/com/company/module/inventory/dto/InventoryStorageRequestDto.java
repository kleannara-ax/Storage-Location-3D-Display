package com.company.module.inventory.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class InventoryStorageRequestDto {

    @NotBlank(message = "Location code is required")
    @Size(max = 50, message = "Location code must be 50 characters or less")
    private String locationCode;

    @NotBlank(message = "Location name is required")
    @Size(max = 200, message = "Location name must be 200 characters or less")
    private String locationName;

    @Size(max = 50, message = "Zone must be 50 characters or less")
    private String zone;

    private Double coordX;
    private Double coordY;
    private Double coordZ;

    @Min(value = 1, message = "Capacity must be at least 1")
    private Integer capacity;
}
