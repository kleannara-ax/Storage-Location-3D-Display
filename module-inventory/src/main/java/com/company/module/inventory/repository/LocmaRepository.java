package com.company.module.inventory.repository;

import com.company.module.inventory.entity.LocmaEntity;
import com.company.module.inventory.entity.LocmaId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LocmaRepository extends JpaRepository<LocmaEntity, LocmaId> {

    /** 거점(WAREKY) 기준 조회 */
    List<LocmaEntity> findByWareky(Integer wareky);

    /** 구역(ZONEKY) 기준 조회 */
    List<LocmaEntity> findByZoneky(String zoneky);

    /** 거점 + 구역 복합 조회 */
    List<LocmaEntity> findByWarekyAndZoneky(Integer wareky, String zoneky);

    /** 영역(AREAKY) 기준 조회 */
    List<LocmaEntity> findByAreaky(String areaky);

    /** 작업구역(TKZONE) 기준 조회 */
    List<LocmaEntity> findByTkzone(String tkzone);

    /** 상태(STATUS) 기준 조회 */
    List<LocmaEntity> findByStatus(Integer status);

    /** 지번유형(LOCATY) 기준 조회 */
    List<LocmaEntity> findByLocaty(Integer locaty);

    /** 지번명(SHORTX) 키워드 검색 */
    @Query("SELECT l FROM LocmaEntity l WHERE l.shortx LIKE %:keyword%")
    List<LocmaEntity> searchByShortx(@Param("keyword") String keyword);

    /** 거점별 지번 수 통계 */
    @Query("SELECT l.wareky, COUNT(l) FROM LocmaEntity l GROUP BY l.wareky ORDER BY l.wareky")
    List<Object[]> countByWareky();

    /** 거점 + 구역별 지번 수 통계 */
    @Query("SELECT l.wareky, l.zoneky, COUNT(l) FROM LocmaEntity l GROUP BY l.wareky, l.zoneky ORDER BY l.wareky, l.zoneky")
    List<Object[]> countByWarekyAndZoneky();
}
