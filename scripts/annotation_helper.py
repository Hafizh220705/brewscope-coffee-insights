#!/usr/bin/env python3
"""
Interactive Annotation Helper for BrewScope ABSA
Membantu anotasi manual dengan interface interaktif dan validasi otomatis
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any


class AnnotationHelper:
    def __init__(self, input_file: str, output_file: str):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.records = []
        self.current_review_idx = 0
        self.aspects = [
            "product_quality",
            "service", 
            "price_value",
            "ambience",
            "facilities",
            "cleanliness"
        ]
        
    def load_records(self):
        """Load JSONL file"""
        print(f"📂 Loading dari: {self.input_file}")
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.records = [json.loads(line) for line in f]
        print(f"✅ Loaded {len(self.records)} records ({len(self.records)//6} reviews)\n")
        
    def save_records(self):
        """Save progress ke output file"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for rec in self.records:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        print(f"💾 Saved to: {self.output_file}")
        
    def find_next_unannotated(self) -> int:
        """Cari review pertama yang belum selesai dianotasi"""
        for i in range(0, len(self.records), 6):
            if self.records[i]['annotation_status'] == 'draft':
                return i // 6
        return len(self.records) // 6  # Semua sudah selesai
        
    def calculate_offset(self, text: str, quote: str) -> tuple:
        """Calculate start and end offset"""
        try:
            start = text.index(quote)
            end = start + len(quote)
            # Validasi
            if text[start:end] == quote:
                return start, end
            else:
                return None, None
        except ValueError:
            return None, None
            
    def annotate_review(self, review_idx: int):
        """Anotasi satu review (6 aspek)"""
        base_idx = review_idx * 6
        review_text = self.records[base_idx]['review_text']
        review_id = self.records[base_idx]['review_id']
        
        print("="*80)
        print(f"📝 REVIEW #{review_idx + 1} of {len(self.records)//6}")
        print(f"ID: {review_id}")
        print("="*80)
        print(f"\n📄 Teks Review:\n\"{review_text}\"\n")
        print("="*80)
        
        # Input untuk 6 aspek
        for i, aspect in enumerate(self.aspects):
            rec_idx = base_idx + i
            print(f"\n🔍 Aspek {i+1}/6: {aspect.upper().replace('_', ' ')}")
            print("-" * 40)
            
            # Input presence
            while True:
                presence = input("Presence (m=mentioned / n=not_mentioned / u=uncertain): ").strip().lower()
                if presence in ['m', 'mentioned']:
                    presence = 'mentioned'
                    break
                elif presence in ['n', 'not_mentioned']:
                    presence = 'not_mentioned'
                    break
                elif presence in ['u', 'uncertain']:
                    presence = 'uncertain'
                    break
                else:
                    print("❌ Input tidak valid! Gunakan m/n/u")
            
            self.records[rec_idx]['aspect_presence'] = presence
            
            # Jika not_mentioned, skip sisanya
            if presence == 'not_mentioned':
                self.records[rec_idx]['sentiment'] = None
                self.records[rec_idx]['mention_type'] = None
                self.records[rec_idx]['evidence'] = []
                self.records[rec_idx]['annotation_status'] = 'completed'
                print("✅ Marked as not_mentioned\n")
                continue
            
            # Input sentiment
            while True:
                sentiment = input("Sentiment (p=positive / neu=neutral / neg=negative / mix=mixed): ").strip().lower()
                if sentiment in ['p', 'positive']:
                    sentiment = 'positive'
                    break
                elif sentiment in ['neu', 'neutral']:
                    sentiment = 'neutral'
                    break
                elif sentiment in ['neg', 'negative']:
                    sentiment = 'negative'
                    break
                elif sentiment in ['mix', 'mixed']:
                    sentiment = None
                    self.records[rec_idx]['mixed_sentiment'] = True
                    break
                else:
                    print("❌ Input tidak valid! Gunakan p/neu/neg/mix")
            
            self.records[rec_idx]['sentiment'] = sentiment
            
            # Input mention type
            while True:
                mention = input("Mention type (e=explicit / i=implicit): ").strip().lower()
                if mention in ['e', 'explicit']:
                    mention = 'explicit'
                    break
                elif mention in ['i', 'implicit']:
                    mention = 'implicit'
                    break
                else:
                    print("❌ Input tidak valid! Gunakan e/i")
                    
            self.records[rec_idx]['mention_type'] = mention
            
            # Input evidence
            evidence_list = []
            
            if self.records[rec_idx]['mixed_sentiment']:
                # Mixed: butuh 2 evidence (pos & neg)
                for sent_type in ['positive', 'negative']:
                    print(f"\n🔖 Evidence untuk sentiment {sent_type}:")
                    quote = input(f"  Quote {sent_type}: ").strip()
                    if quote:
                        start, end = self.calculate_offset(review_text, quote)
                        if start is not None:
                            target = input(f"  Target (apa yang dinilai? contoh: kopi, wifi, tempat): ").strip()
                            if not target:
                                target = aspect  # Fallback ke aspect name jika kosong
                            evidence_list.append({
                                "quote": quote,
                                "start": start,
                                "end": end,
                                "opinion_sentiment": sent_type,
                                "mention_type": mention,
                                "target": target
                            })
                            print(f"  ✅ Offset: [{start}:{end}] → \"{review_text[start:end]}\"")
                        else:
                            print(f"  ❌ Quote tidak ditemukan dalam teks!")
            else:
                # Single sentiment
                print("\n🔖 Evidence:")
                quote = input("  Quote: ").strip()
                if quote:
                    start, end = self.calculate_offset(review_text, quote)
                    if start is not None:
                        target = input("  Target (apa yang dinilai? contoh: kopi, wifi, tempat): ").strip()
                        if not target:
                            target = aspect  # Fallback ke aspect name jika kosong
                        evidence_list.append({
                            "quote": quote,
                            "start": start,
                            "end": end,
                            "opinion_sentiment": sentiment,
                            "mention_type": mention,
                            "target": target
                        })
                        print(f"  ✅ Offset: [{start}:{end}] → \"{review_text[start:end]}\"")
                    else:
                        print(f"  ❌ Quote tidak ditemukan dalam teks!")
                        print(f"  💡 Pastikan quote exact match dengan teks!")
            
            self.records[rec_idx]['evidence'] = evidence_list
            
            # Notes (opsional)
            if presence == 'uncertain':
                notes = input("📝 Notes (wajib untuk uncertain): ").strip()
                self.records[rec_idx]['notes'] = notes
            
            # Mark completed
            self.records[rec_idx]['annotation_status'] = 'completed'
            print("✅ Aspek completed!\n")
        
        print("\n" + "="*80)
        print("🎉 Review completed! Saving progress...")
        self.save_records()
        
        # Tanya lanjut atau tidak
        print("\nOpsi:")
        print("  [Enter] = Lanjut ke review berikutnya")
        print("  q = Quit (save & exit)")
        print("  s = Skip ke review tertentu")
        
        choice = input("\nPilihan: ").strip().lower()
        return choice
        
    def run(self):
        """Main loop"""
        print("\n" + "="*80)
        print("🚀 BrewScope Interactive Annotation Helper")
        print("="*80 + "\n")
        
        self.load_records()
        
        # Cari progress terakhir
        self.current_review_idx = self.find_next_unannotated()
        total_reviews = len(self.records) // 6
        
        if self.current_review_idx >= total_reviews:
            print("✅ Semua review sudah selesai dianotasi!")
            return
        
        print(f"📊 Progress: {self.current_review_idx}/{total_reviews} reviews completed")
        print(f"▶️  Starting from review #{self.current_review_idx + 1}\n")
        
        # Loop anotasi
        while self.current_review_idx < total_reviews:
            choice = self.annotate_review(self.current_review_idx)
            
            if choice == 'q':
                print("\n👋 Exiting... Progress saved!")
                break
            elif choice == 's':
                target = input("Skip ke review #: ").strip()
                try:
                    self.current_review_idx = int(target) - 1
                    if self.current_review_idx < 0 or self.current_review_idx >= total_reviews:
                        print("❌ Invalid review number!")
                        self.current_review_idx = self.find_next_unannotated()
                except ValueError:
                    print("❌ Invalid input!")
            else:
                self.current_review_idx += 1
                
        print("\n" + "="*80)
        print("🎊 Annotation session completed!")
        print(f"📁 Output: {self.output_file}")
        print("="*80)


def main():
    """Entry point"""
    print("\n🎯 BrewScope Annotation Helper")
    print("=" * 80)
    
    # Tanya file input
    print("\nOpsi input file:")
    print("  1 = Calibration (50 reviews)")
    print("  2 = Independent (200 reviews)")
    print("  3 = Custom path")
    
    choice = input("\nPilih (1/2/3): ").strip()
    
    if choice == '1':
        input_file = "data/interim/human_annotations/work/robi/robi_calibration.jsonl"
        output_file = "data/interim/human_annotations/work/robi/robi_calibration.jsonl"
    elif choice == '2':
        input_file = "data/interim/human_annotations/work/robi/robi_independent.jsonl"
        output_file = "data/interim/human_annotations/work/robi/robi_independent.jsonl"
    else:
        input_file = input("Input file path: ").strip()
        output_file = input("Output file path (Enter = sama dengan input): ").strip()
        if not output_file:
            output_file = input_file
    
    # Jalankan helper
    helper = AnnotationHelper(input_file, output_file)
    helper.run()


if __name__ == "__main__":
    main()
