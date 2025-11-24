"""
Vendor Routes
==============
Upload vendor files and run matching.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import io

from api.services.vendor_service import VendorService

router = APIRouter()


def get_vendor_service() -> VendorService:
    return VendorService()


@router.post("/upload")
async def upload_vendor_file(
    file: UploadFile = File(...),
    vendor: str = Form(...)
):
    """
    Upload a vendor price list file.

    - **file**: CSV file with vendor products
    - **vendor**: Vendor name (SYSCO or Shamrock)
    """
    if vendor.upper() not in ['SYSCO', 'SHAMROCK']:
        raise HTTPException(status_code=400, detail="Vendor must be 'SYSCO' or 'Shamrock'")

    content = await file.read()
    service = get_vendor_service()
    result = service.parse_vendor_file(content, vendor)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error', 'Failed to parse file'))

    return result


@router.get("/preview/{vendor}")
async def get_vendor_preview(vendor: str):
    """Get preview of uploaded vendor data"""
    service = get_vendor_service()

    if vendor.upper() == 'SYSCO':
        items = service.sysco_products[:20]
    else:
        items = service.shamrock_products[:20]

    return {
        'vendor': vendor,
        'items': items,
        'total': len(service.sysco_products if vendor.upper() == 'SYSCO' else service.shamrock_products)
    }


@router.post("/match")
async def run_matching():
    """
    Run matching between uploaded vendor files.

    Both SYSCO and Shamrock files must be uploaded first.
    """
    service = get_vendor_service()
    result = service.run_matching()

    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('error'))

    return result


@router.get("/matches")
async def get_matches():
    """Get current match results"""
    service = get_vendor_service()
    return {
        'matches': service.get_matches(),
        'summary': service.get_comparison_summary()
    }


@router.get("/export")
async def export_matches():
    """Export match results to CSV"""
    service = get_vendor_service()
    csv_content = service.export_matches_csv()

    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vendor_matches.csv"}
    )


@router.get("/comparison")
async def get_comparison():
    """Get vendor comparison summary"""
    service = get_vendor_service()
    return service.get_comparison_summary()
