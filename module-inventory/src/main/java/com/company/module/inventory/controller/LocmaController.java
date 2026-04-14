package com.company.module.inventory.controller;

import com.company.module.inventory.dto.LocmaRequestDto;
import com.company.module.inventory.dto.LocmaResponseDto;
import com.company.module.inventory.service.LocmaService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * LOCMA (Location Master) REST Controller.
 * URL API Prefix: /inventory-api/locma/**
 * No @Transactional here - transactions are managed in Service layer only.
 */
@RestController
@RequestMapping("/inventory-api/locma")
@RequiredArgsConstructor
public class LocmaController {

    private final LocmaService locmaService;

    // ============================================================
    // GET endpoints
    // ============================================================

    /** 전체 LOCMA 조회 */
    @GetMapping
    public ResponseEntity<List<LocmaResponseDto>> findAll() {
        return ResponseEntity.ok(locmaService.findAll());
    }

    /** 복합키(거점+지번) 단건 조회 */
    @GetMapping("/{wareky}/{locaky}")
    public ResponseEntity<LocmaResponseDto> findById(
            @PathVariable Integer wareky,
            @PathVariable String locaky) {
        return ResponseEntity.ok(locmaService.findById(wareky, locaky));
    }

    /** 거점(WAREKY) 기준 조회 */
    @GetMapping("/wareky/{wareky}")
    public ResponseEntity<List<LocmaResponseDto>> findByWareky(@PathVariable Integer wareky) {
        return ResponseEntity.ok(locmaService.findByWareky(wareky));
    }

    /** 구역(ZONEKY) 기준 조회 */
    @GetMapping("/zoneky/{zoneky}")
    public ResponseEntity<List<LocmaResponseDto>> findByZoneky(@PathVariable String zoneky) {
        return ResponseEntity.ok(locmaService.findByZoneky(zoneky));
    }

    /** 거점 + 구역 복합 조회 */
    @GetMapping("/wareky/{wareky}/zoneky/{zoneky}")
    public ResponseEntity<List<LocmaResponseDto>> findByWarekyAndZoneky(
            @PathVariable Integer wareky,
            @PathVariable String zoneky) {
        return ResponseEntity.ok(locmaService.findByWarekyAndZoneky(wareky, zoneky));
    }

    /** 영역(AREAKY) 기준 조회 */
    @GetMapping("/areaky/{areaky}")
    public ResponseEntity<List<LocmaResponseDto>> findByAreaky(@PathVariable String areaky) {
        return ResponseEntity.ok(locmaService.findByAreaky(areaky));
    }

    /** 상태(STATUS) 기준 조회 */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<LocmaResponseDto>> findByStatus(@PathVariable Integer status) {
        return ResponseEntity.ok(locmaService.findByStatus(status));
    }

    /** 지번명(SHORTX) 키워드 검색 */
    @GetMapping("/search")
    public ResponseEntity<List<LocmaResponseDto>> searchByShortx(
            @RequestParam String keyword) {
        return ResponseEntity.ok(locmaService.searchByShortx(keyword));
    }

    /** 거점별 지번 수 통계 */
    @GetMapping("/stats/count-by-wareky")
    public ResponseEntity<List<Map<String, Object>>> countByWareky() {
        return ResponseEntity.ok(locmaService.countByWareky());
    }

    // ============================================================
    // POST / PUT / DELETE endpoints
    // ============================================================

    /** 신규 LOCMA 등록 */
    @PostMapping
    public ResponseEntity<LocmaResponseDto> create(
            @Valid @RequestBody LocmaRequestDto requestDto) {
        LocmaResponseDto created = locmaService.create(requestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    /** LOCMA 수정 */
    @PutMapping("/{wareky}/{locaky}")
    public ResponseEntity<LocmaResponseDto> update(
            @PathVariable Integer wareky,
            @PathVariable String locaky,
            @Valid @RequestBody LocmaRequestDto requestDto) {
        return ResponseEntity.ok(locmaService.update(wareky, locaky, requestDto));
    }

    /** LOCMA 삭제 */
    @DeleteMapping("/{wareky}/{locaky}")
    public ResponseEntity<Void> delete(
            @PathVariable Integer wareky,
            @PathVariable String locaky) {
        locmaService.delete(wareky, locaky);
        return ResponseEntity.noContent().build();
    }
}
