package com.company.module.inventory.service;

import com.company.module.inventory.dto.InventoryStorageRequestDto;
import com.company.module.inventory.dto.InventoryStorageResponseDto;
import com.company.module.inventory.entity.InventoryStorageEntity;
import com.company.module.inventory.repository.InventoryStorageRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("InventoryStorageService Unit Tests")
class InventoryStorageServiceTest {

    @Mock
    private InventoryStorageRepository inventoryStorageRepository;

    @InjectMocks
    private InventoryStorageService inventoryStorageService;

    private InventoryStorageEntity sampleEntity;
    private InventoryStorageRequestDto sampleRequest;

    @BeforeEach
    void setUp() {
        sampleEntity = InventoryStorageEntity.builder()
                .locationId(1L)
                .locationCode("LOC-TEST-01")
                .locationName("Test Location Zone A")
                .zone("ZONE-A")
                .coordX(1.0)
                .coordY(2.0)
                .coordZ(3.0)
                .capacity(100)
                .currentUsage(50)
                .useYn("Y")
                .build();

        sampleRequest = InventoryStorageRequestDto.builder()
                .locationCode("LOC-TEST-01")
                .locationName("Test Location Zone A")
                .zone("ZONE-A")
                .coordX(1.0)
                .coordY(2.0)
                .coordZ(3.0)
                .capacity(100)
                .build();
    }

    @Test
    @DisplayName("Should return all storage locations")
    void findAll_ShouldReturnAllLocations() {
        // given
        when(inventoryStorageRepository.findAll()).thenReturn(Arrays.asList(sampleEntity));

        // when
        List<InventoryStorageResponseDto> result = inventoryStorageService.findAll();

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getLocationCode()).isEqualTo("LOC-TEST-01");
    }

    @Test
    @DisplayName("Should return storage location by ID")
    void findById_ShouldReturnLocation() {
        // given
        when(inventoryStorageRepository.findById(1L)).thenReturn(Optional.of(sampleEntity));

        // when
        InventoryStorageResponseDto result = inventoryStorageService.findById(1L);

        // then
        assertThat(result.getLocationId()).isEqualTo(1L);
        assertThat(result.getCoordX()).isEqualTo(1.0);
        assertThat(result.getCoordY()).isEqualTo(2.0);
        assertThat(result.getCoordZ()).isEqualTo(3.0);
    }

    @Test
    @DisplayName("Should throw exception when location not found")
    void findById_ShouldThrowException_WhenNotFound() {
        // given
        when(inventoryStorageRepository.findById(999L)).thenReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> inventoryStorageService.findById(999L))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Storage location not found with id: 999");
    }

    @Test
    @DisplayName("Should create new storage location")
    void create_ShouldCreateLocation() {
        // given
        when(inventoryStorageRepository.existsByLocationCode(anyString())).thenReturn(false);
        when(inventoryStorageRepository.save(any(InventoryStorageEntity.class))).thenReturn(sampleEntity);

        // when
        InventoryStorageResponseDto result = inventoryStorageService.create(sampleRequest);

        // then
        assertThat(result.getLocationCode()).isEqualTo("LOC-TEST-01");
        assertThat(result.getCapacity()).isEqualTo(100);
        verify(inventoryStorageRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("Should throw exception on duplicate location code")
    void create_ShouldThrowException_WhenDuplicateCode() {
        // given
        when(inventoryStorageRepository.existsByLocationCode("LOC-TEST-01")).thenReturn(true);

        // when & then
        assertThatThrownBy(() -> inventoryStorageService.create(sampleRequest))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Location code already exists");
    }

    @Test
    @DisplayName("Should find available storage locations")
    void findAvailableLocations_ShouldReturnAvailable() {
        // given
        when(inventoryStorageRepository.findAvailableLocations())
                .thenReturn(Arrays.asList(sampleEntity));

        // when
        List<InventoryStorageResponseDto> result = inventoryStorageService.findAvailableLocations();

        // then
        assertThat(result).hasSize(1);
        assertThat(result.get(0).getCurrentUsage()).isLessThan(result.get(0).getCapacity());
    }

    @Test
    @DisplayName("Should soft-delete storage location")
    void delete_ShouldSoftDeleteLocation() {
        // given
        when(inventoryStorageRepository.findById(1L)).thenReturn(Optional.of(sampleEntity));
        when(inventoryStorageRepository.save(any(InventoryStorageEntity.class))).thenReturn(sampleEntity);

        // when
        inventoryStorageService.delete(1L);

        // then
        assertThat(sampleEntity.getUseYn()).isEqualTo("N");
        verify(inventoryStorageRepository, times(1)).save(any());
    }
}
