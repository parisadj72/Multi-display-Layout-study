using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

[RequireComponent(typeof(CanvasGroup))]
public class DragUI : MonoBehaviour, IBeginDragHandler, IDragHandler, IEndDragHandler
{
    private void Awake()
    {

    }
    void Start()
    {
    }

    public void OnBeginDrag(PointerEventData eventData)
    {
        print("OnBeginDrag");
        //GetComponent<CanvasGroup>().blocksRaycasts = false;
    }

    public void OnDrag(PointerEventData eventData)
    {
        if (eventData.pointerCurrentRaycast.isValid)
        {
            print("OnDrag");
            var currentRaycastPosition = eventData.pointerCurrentRaycast.worldPosition;
            transform.position = currentRaycastPosition;
        }
    }

    public void OnEndDrag(PointerEventData eventData)
    {
        print("OnEndDrag");
        GetComponent<CanvasGroup>().blocksRaycasts = true;
    }

}
