export interface ScrapedPost {
  id: string;
  shortcode: string;
  caption: string | null;
  imageUrl: string;
  takenAt: string;
  likeCount: number;
  commentCount: number;
  isVideo: boolean;
}
