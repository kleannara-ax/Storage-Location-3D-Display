package com.company.module.inventory.service;

import com.company.module.inventory.dto.LocmaRequestDto;
import com.company.module.inventory.dto.LocmaResponseDto;
import com.company.module.inventory.entity.LocmaEntity;
import com.company.module.inventory.entity.LocmaId;
import com.company.module.inventory.repository.LocmaRepository;
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
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@DisplayName("LocmaService Unit Tests")
class LocmaServiceTest {

    @Mock
    private LocmaRepository locmaRepository;

    @InjectMocks
    private LocmaService locmaService;

    private LocmaEntity sampleEntity;
    private LocmaRequestDto sampleRequest;

    @BeforeEach
    void setUp() {
        sampleEntity = LocmaEntity.builder()
                .wareky(1100)
                .locaky("A30-30-06")
                .locaty(10)
                .shortx("중문30")
                .taskty(" ")
                .zoneky("A30")
                .areaky("280")
                .tkzone("A30")
                .status(40)
                .ibrout(9999999999L)
                .obrout(9999999999L)
                .rprout(9999999999L)
                .mixsku("V")
                .mixlot("V")
                .credat(20220914)
                .cretim(100000)
                .creusr("HNW9")
                .lmodat(20220914)
                .lmotim(100000)
                .lmousr("HNW9")
                .updchk(0)
                .build();

        sampleRequest = LocmaRequestDto.builder()
                .wareky(1100)
                .locaky("A30-30-06")
                .locaty(10)
                .shortx("중문30")
                .zoneky("A30")
                .areaky("280")
                .status(40)
                .build();
    }

    @Test
    @DisplayName("전체 LOCMA 조회")
    void findAll_ShouldReturnAll() {
        when(locmaRepository.findAll()).thenReturn(Arrays.asList(sampleEntity));

        List<LocmaResponseDto> result = locmaService.findAll();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getWareky()).isEqualTo(1100);
        assertThat(result.get(0).getLocaky()).isEqualTo("A30-30-06");
    }

    @Test
    @DisplayName("복합키(WAREKY+LOCAKY) 단건 조회")
    void findById_ShouldReturnEntity() {
        LocmaId id = new LocmaId(1100, "A30-30-06");
        when(locmaRepository.findById(id)).thenReturn(Optional.of(sampleEntity));

        LocmaResponseDto result = locmaService.findById(1100, "A30-30-06");

        assertThat(result.getWareky()).isEqualTo(1100);
        assertThat(result.getLocaky()).isEqualTo("A30-30-06");
        assertThat(result.getShortx()).isEqualTo("중문30");
        assertThat(result.getStatus()).isEqualTo(40);
    }

    @Test
    @DisplayName("존재하지 않는 LOCMA 조회 시 예외")
    void findById_ShouldThrow_WhenNotFound() {
        LocmaId id = new LocmaId(9999, "XXX");
        when(locmaRepository.findById(id)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> locmaService.findById(9999, "XXX"))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("LOCMA not found");
    }

    @Test
    @DisplayName("거점(WAREKY) 기준 조회")
    void findByWareky_ShouldReturnList() {
        when(locmaRepository.findByWareky(1100)).thenReturn(Arrays.asList(sampleEntity));

        List<LocmaResponseDto> result = locmaService.findByWareky(1100);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getWareky()).isEqualTo(1100);
    }

    @Test
    @DisplayName("구역(ZONEKY) 기준 조회")
    void findByZoneky_ShouldReturnList() {
        when(locmaRepository.findByZoneky("A30")).thenReturn(Arrays.asList(sampleEntity));

        List<LocmaResponseDto> result = locmaService.findByZoneky("A30");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getZoneky()).isEqualTo("A30");
    }

    @Test
    @DisplayName("상태(STATUS) 기준 조회")
    void findByStatus_ShouldReturnList() {
        when(locmaRepository.findByStatus(40)).thenReturn(Arrays.asList(sampleEntity));

        List<LocmaResponseDto> result = locmaService.findByStatus(40);

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getStatus()).isEqualTo(40);
    }

    @Test
    @DisplayName("신규 LOCMA 등록")
    void create_ShouldCreateEntity() {
        when(locmaRepository.existsById(any(LocmaId.class))).thenReturn(false);
        when(locmaRepository.save(any(LocmaEntity.class))).thenReturn(sampleEntity);

        LocmaResponseDto result = locmaService.create(sampleRequest);

        assertThat(result.getWareky()).isEqualTo(1100);
        assertThat(result.getLocaky()).isEqualTo("A30-30-06");
        verify(locmaRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("중복 LOCMA 등록 시 예외")
    void create_ShouldThrow_WhenDuplicate() {
        when(locmaRepository.existsById(any(LocmaId.class))).thenReturn(true);

        assertThatThrownBy(() -> locmaService.create(sampleRequest))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("already exists");
    }

    @Test
    @DisplayName("LOCMA 수정")
    void update_ShouldUpdateEntity() {
        LocmaId id = new LocmaId(1100, "A30-30-06");
        when(locmaRepository.findById(id)).thenReturn(Optional.of(sampleEntity));
        when(locmaRepository.save(any(LocmaEntity.class))).thenReturn(sampleEntity);

        LocmaResponseDto result = locmaService.update(1100, "A30-30-06", sampleRequest);

        assertThat(result).isNotNull();
        verify(locmaRepository, times(1)).save(any());
    }

    @Test
    @DisplayName("LOCMA 삭제")
    void delete_ShouldDeleteEntity() {
        LocmaId id = new LocmaId(1100, "A30-30-06");
        when(locmaRepository.existsById(id)).thenReturn(true);
        doNothing().when(locmaRepository).deleteById(id);

        locmaService.delete(1100, "A30-30-06");

        verify(locmaRepository, times(1)).deleteById(id);
    }

    @Test
    @DisplayName("지번명 키워드 검색")
    void searchByShortx_ShouldReturnMatching() {
        when(locmaRepository.searchByShortx("중문")).thenReturn(Arrays.asList(sampleEntity));

        List<LocmaResponseDto> result = locmaService.searchByShortx("중문");

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getShortx()).contains("중문");
    }
}
