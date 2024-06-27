using System.Collections;
using System.Collections.Generic;
using Unity.XR.CoreUtils;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.XR;
using UnityEngine.UIElements;
using UnityEngine.XR;
using UnityEngine.XR.ARSubsystems;
using UnityEngine.XR.Interaction.Toolkit.Inputs;

public class DragUI : MonoBehaviour, IBeginDragHandler, IDragHandler, IEndDragHandler
{

    public GameObject child;
    public Transform parent;
    public Transform previousParent;

    public Transform leftStabilizer;
    public Transform rightStabilizer;

    private void Awake()
    {

    }
    void Start()
    {
    }

    public void OnBeginDrag(PointerEventData eventData)
    {
        //print("OnBeginDrag");
        //GetComponent<CanvasGroup>().blocksRaycasts = false;
    }

    public void OnDrag(PointerEventData eventData)
    {
        if (eventData.pointerCurrentRaycast.isValid)
        {
            print(InputDeviceRole.LeftHanded);
            print("OnDrag");
            //var currentRaycastPosition = eventData.pointerCurrentRaycast.worldPosition;
            //transform.position = currentRaycastPosition;
            child.transform.SetParent(parent);

        }
    }

    public void OnEndDrag(PointerEventData eventData)
    {
        //print("OnEndDrag");
        //GetComponent<CanvasGroup>().blocksRaycasts = true;
        child.transform.SetParent(previousParent);
    }

}
