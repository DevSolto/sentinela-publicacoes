import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import instagramConfig from './config/instagram.config';
import { HealthModule } from './health/health.module';
import { ScraperModule } from './scraper/scraper.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      load: [instagramConfig],
    }),
    HealthModule,
    ScraperModule,
  ],
})
export class AppModule {}
