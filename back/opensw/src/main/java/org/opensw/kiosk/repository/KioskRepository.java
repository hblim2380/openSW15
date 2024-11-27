package org.opensw.kiosk.repository;

import org.opensw.kiosk.entity.Menu;
import org.springframework.data.jpa.repository.JpaRepository;

public interface KioskRepository extends JpaRepository<Menu, Long> {
}
