using System.Collections;
using System.Collections.Generic;
using Unity.XR.CoreUtils;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.XR;
using UnityEngine.UIElements;
using UnityEngine.XR;
using UnityEngine.XR.ARSubsystems;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.Inputs;
using UnityEngine.XR.Interaction.Toolkit.UI;

public class DragUI : MonoBehaviour, IBeginDragHandler, IDragHandler, IEndDragHandler
{

    public GameObject child;
    private Transform parent;
    public Transform previousParent;

    public Transform leftStabilizer;
    public Transform rightStabilizer;

    private string leftController;
    private string rightController;

    private void Awake()
    {

    }
    void Start()
    {
    }

    public void OnBeginDrag(PointerEventData eventData)
    {
        if (eventData.pointerCurrentRaycast.isValid)
        {
            print("OnDrag");
            if (eventData is TrackedDeviceEventData trackedDeviceEventData)
            {
                if (trackedDeviceEventData.interactor is XRBaseControllerInteractor xrInteractor)
                {
                    // Your code, for example haptic or compare the interactor to left / right
                    print(xrInteractor.name);

                    if (xrInteractor.name == "RayInteractorLeft")
                    {
                        parent = leftStabilizer;
                    }
                    else if (xrInteractor.name == "RayInteractorRight")
                    {
                        parent = rightStabilizer;
                    }
                    //xrInteractor.SendHapticImpulse(0.25f, 0.25f);
                }
            }
            //var currentRaycastPosition = eventData.pointerCurrentRaycast.worldPosition;
            //transform.position = currentRaycastPosition;

        }
        //print("OnBeginDrag");
        //GetComponent<CanvasGroup>().blocksRaycasts = false;
    }

    public void OnDrag(PointerEventData eventData)
    {

        child.transform.SetParent(parent);
    }

    public void OnEndDrag(PointerEventData eventData)
    {
        //print("OnEndDrag");
        //GetComponent<CanvasGroup>().blocksRaycasts = true;
        child.transform.SetParent(previousParent);
        parent = null;
    }

    void OnEnable()
    {
        InputDevices.deviceConnected += DeviceConnected;
        List<InputDevice> devices = new List<InputDevice>();
        InputDevices.GetDevices(devices);
        foreach (var device in devices)
            DeviceConnected(device);
    }
    void OnDisable()
    {
        InputDevices.deviceConnected -= DeviceConnected;
    }
    void DeviceConnected(InputDevice device)
    {
        // The Left Hand
        if ((device.characteristics & InputDeviceCharacteristics.Left) != 0)
        {
            leftController = device.name;
            //print(leftController);
        }
        // The Right hand
        else if ((device.characteristics & InputDeviceCharacteristics.Right) != 0)
        {
            rightController = device.name;
            //print(rightController);
        }
    }
}
